## Copyright (c) 2015 SONATA-NFV, 2017 5GTANGO [, ANY ADDITIONAL AFFILIATION]
## ALL RIGHTS RESERVED.
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
## Neither the name of the SONATA-NFV, 5GTANGO [, ANY ADDITIONAL AFFILIATION]
## nor the names of its contributors may be used to endorse or promote
## products derived from this software without specific prior written
## permission.
##
## This work has been performed in the framework of the SONATA project,
## funded by the European Commission under Grant number 671517 through
## the Horizon 2020 and 5G-PPP programmes. The authors would like to
## acknowledge the contributions of their colleagues of the SONATA
## partner consortium (www.sonata-nfv.eu).
##
## This work has been performed in the framework of the 5GTANGO project,
## funded by the European Commission under Grant number 761493 through
## the Horizon 2020 and 5G-PPP programmes. The authors would like to
## acknowledge the contributions of their colleagues of the 5GTANGO
## partner consortium (www.5gtango.eu).

# Use an official Python runtime as a parent image
FROM python:3.7-slim

# Copy the current directory contents into the container at /app
ADD . /app

# Set the working directory to /app
WORKDIR /app

# Set Mongo Instance Environment Variables
ENV DATABASE_HOST mongo
ENV DATABASE_NAME tng-sdk-analyze-weight
ENV DATABASE_PORT 27017

# Set Catalogue Environment Variables
ENV CATALOGUES_URL http://tng-cat:4011/catalogues/api/v2/

# Set MONITORING URL Environment Variables
ENV MONITORING_URL http://son-monitor-manager:8000/api/v1/

# Set Db/Collections Environment Variables
ENV DICT_COLL dictionaries
ENV UNK_COLL unknown_vnfs

#Set Log Level Environment Variable
ENV LOG_LEVEL INFO

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 8084 available to the world outside this container
EXPOSE 8084

# Run app.py when the container launches
CMD ["python", "main.py"]
