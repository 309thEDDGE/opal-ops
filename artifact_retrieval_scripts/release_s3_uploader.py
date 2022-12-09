#!/usr/bin/env python3
import pathlib
import os
import sys
import subprocess
import docker
import boto3
from botocore.exceptions import ClientError
from dotenv import dotenv_values
import tarfile
import shutil
import yaml
import bz2

'''
system_requirements:

Access to the opal-artifact-downloader ec2 instance

pip
 - python-dotenv
 - docker
 - boto3
 - awscli
 - urllib3
 - requests
 - yaml

(requests and urllib3 may need to be reinstalled w/ pip install --upgrade <package>, due 
to some import failures)

opal-ops repo 
'''

# Should this be expected to be run in a specific ec2 instance we've provisioned?
# This would likely solve any issue of people needing credentials for our account,
# we can instead provide an ssh key (or something)
# in future could be good to set up like a lambda function that takes input of the tag to grab and goes from there
# if no tag is provided, just go with the most recent tag on the repo and pull those images


'''
s3 structure:
    <release_tag_1>(dir)
        opal-ops(tag_1)
        containers(tag_1)
    <release_tag_2>
    <release_tag_n>

    docker-compose binary
    rhel iso
    docker binary


'''

#one of these functions can probably be deleted
def b_to_gb(bytes_in):
    gb_rate = 1 / (1024**3)
    return bytes_in * gb_rate

def gb_to_b(bytes_in):
    return bytes_in * (1024**3)

class artifact_setter_upper():
    def __init__(self, release_tag, max_file_size):
        #set default value to 4gb if string is empty
        if max_file_size == '':
            self.max_file_size = 4
        else:
            self.max_file_size = int(max_file_size)

        self.working_dir = self.init_temp_directory()
        self.bucket_name = 'FILL THIS IN'
        self.version_tag = release_tag
        self.split_files_dict={}
        self.docker_client = docker.from_env(timeout=900)
        self.s3_client = boto3.client('s3', region_name='FILL THIS IN')
        self.opal_ops_path = self.working_dir / 'opal-ops' 
        self.artifact_tar_path = self.working_dir / 'saved_docker_images'
        self.default_env_path = self.opal_ops_path / 'docker-compose' / '.env'
        self.check_directories_exist()

    def get_docker_image_tags(self):
        config = dotenv_values(self.default_env_path)

        image_dict = {k:v for k, v in config.items() if "_IMAGE" in k}
        return image_dict


    # create a temp directory for all artifacts to be gathered and cd into it
    def init_temp_directory(self):
        # gets the parent directory containing opal-ops
        working_path = pathlib.Path('../..')
        return working_path.resolve()

    def check_directories_exist(self):
        if not os.path.exists(self.opal_ops_path):
            print("how are you even running this script? go clone the repo down and run this from there")
            exit(1)
        if not os.path.exists(self.artifact_tar_path):
            os.mkdir(self.artifact_tar_path)
        # not going to check if the working directory exists, because if it doesn't, that
        # would imply it's suddenly vanished and you probably have bigger fish to fry
        # than uploading some silly tarballs



    ## this may be better suited as a function to run in a bash script, to take agency away from the user
    #def checkout_version_tag(self):
        ## should this just grab the latest tag if nothing was specified?
        #prev_dir = pathlib.Path('.')
        #os.chdir(self.opal_ops_path)
        #subprocess.Popen('git checkout {}'.format(self.version_tag),shell=True).wait()
        #os.chdir(prev_dir)


    def tar_ops_repo(self):
        os.chdir(self.working_dir)
        with tarfile.open(self.artifact_tar_path / "opal-ops.tar.gz", "w:gz") as tar:
            #tar.add(self.opal_ops_path)
            tar.add("opal-ops")


    def pull_docker_artifacts(self):
        self.docker_images = self.get_docker_image_tags()
        print("Found docker images:")
        for var, img in self.docker_images.items():
            print(f"\t{var} = {img}")

        # https://docker-py.readthedocs.io/en/stable/
        for image_name in self.docker_images.values():

            if ":" in image_name:
                repo, tag = image_name.split(":")
            else:
                repo = image_name
                tag = ""

            # docker.pull returns an image object
            # https://docker-py.readthedocs.io/en/stable/images.html#docker.models.images.ImageCollection.pull
            try:
                img = self.docker_client.images.pull(repo, tag)
                print(f"\nPulling {image_name} ...")
            except docker.errors.APIError:
                print("You need to log in to registry1 yourself dingus")
                exit(1)

            repo_save_name = repo.split("/")[-1]

            with open(self.artifact_tar_path / f"{repo_save_name}.tar", "wb") as f:
                print(f"Saving to {repo_save_name}.tar ...")
                for chunk in img.save(named=True):
                    f.write(chunk)
                print("Save complete")

        print("All images pulled!")

    
    def bzip_files(self):
        print("Compressing files...")
        #will also remove the original version of the file
        compression_level = 7
        os.chdir(self.artifact_tar_path)

        for file in self.artifact_tar_path.glob('*'):
            with open(f"{file}.bz2", 'wb') as out_file:
                with open(file, 'rb') as in_file:
                    print(f"Writing to {file.name}.bz2")
                    out_file.write(bz2.compress(in_file.read(),compression_level))
            print(f"Removing original file {file.name}")
            file.unlink()
                
                

    def split_large_files(self):
        print("Prepping to split large files...")
        #large_files = []
        #for file in self.artifact_tar_path.rglob('*'):
            #if file.stat().st_size > 
        large_files = [
            file for file in self.artifact_tar_path.glob('*') \
            if b_to_gb(file.stat().st_size) >= self.max_file_size
        ]
        for file in large_files:
            print(f"Splitting {file}")
            subprocess.Popen(f"split --verbose -b {self.max_file_size}GB {file} {file}.",shell=True).wait()
            # split file
        with open(self.artifact_tar_path / "split_file_names.txt", "w") as f:
            print("Storing list of split files for later use")
            for file in large_files:
                f.write(f"{file}\n")


    def generate_file_manifest(self):
        os.chdir(self.artifact_tar_path)
        print("Generating file manifest...")

        with open(self.artifact_tar_path / f"file_manifest_{self.version_tag}.yml",'w') as f:
            file_list =  [file.name for file in self.artifact_tar_path.glob('*')]
            f.write(yaml.dump(list(file_list),default_flow_style=False,allow_unicode=False))



    # mod_name is used to indicate whether the checksum is used upon initial retrieval or 
    # once files are in place in the 
    def generate_checksums(self,mod_name=''):
        os.chdir(self.artifact_tar_path)
        print("Generating checksums")
        subprocess.Popen(['/bin/md5sum ./* > md5sums_{}'.format(self.version_tag)],shell=True).wait()
        print("Checksum file generated")
        subprocess.Popen(['/bin/cat md5sums_{}'.format(self.version_tag)],shell=True).wait()

        print('Validating checksums as a sanity check')
        output = subprocess.Popen(['/bin/md5sum -c md5sums_{}'.format(self.version_tag)],shell=True)
        output.wait()
        if output.returncode == 0:
            print("Sanity check passed")
        else:
            print("Files don't pass their own checksums")
            print("Something is very wrong here")
            raise Exception("AAAAAAAAAAAAAAAAAAAAAA")


    def upload_files(self):
        # upload individually to allow retries (do we even want this?)
        # self.s3_client
        # use self.version_tag
        ctr = 0
        for file in self.artifact_tar_path.glob('*'):
            try:
                in_file = file.name
                print(f"Uploading {in_file} to {self.bucket_name}")
                self.s3_client.upload_file(str(file),self.bucket_name,f"{self.version_tag}/{in_file}")
            except Exception as e:
                print(e)
        
    def cleanup(self):
        os.chdir(self.working_dir)
        print("Removing local files")
        shutil.rmtree(self.artifact_tar_path)

if __name__ == "__main__":
    # this section is if using bash script to run
    tag = ""
    filesize = ""
    if len(sys.argv) == 3:
        tag = sys.argv[1]
        filesize = sys.argv[2]
    else: 
        # this section is if running python script directly. Has less input validation
        # (know what you are doing)
        
        # if running this script directly, this tag is just what you want to call the directory on upload. 
        # It will just take the current working state of the opal-ops repo. 
        # Primarily for testing purposes 
        # Please follow the [yyyy.mm.dd] format to allow tests of downloads 
        print("Name of directory in s3 to upload to: ")
        tag = input()
        # gb seems like a reasonable unit here. If you need to break files up files into smaller segments than 
        # 1gb, you should probably consider what life choices led you to a situation in which floppy disks
        # are still used, and perhaps asking someone in your favorite IRC channel what a DVD is.
        print("Maximum filesize in GB:\n(leave empty for 4G)\n(input will be rounded down)")
        filesize = input()
    
    art = artifact_setter_upper(release_tag = tag, max_file_size = filesize)
    art.pull_docker_artifacts()
    art.tar_ops_repo()
    art.bzip_files()
    art.split_large_files()
    art.generate_file_manifest()
    art.generate_checksums()
    art.upload_files()
    art.cleanup()

