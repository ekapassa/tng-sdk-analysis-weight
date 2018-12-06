<p align="center"><img src="https://github.com/sonata-nfv/tng-api-gtw/wiki/images/sonata-5gtango-logo-500px.png"/></p>

# tng-sdk-analyze-weight [![Build Status](https://jenkins.sonata-nfv.eu/buildStatus/icon?job=tng-sdk-analyze-weight/master)](https://jenkins.sonata-nfv.eu/job/tng-sdk-analyze-weight/job/master/)   [![Join the chat at https://gitter.im/sonata-nfv/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/sonata-nfv/Lobby)

5GTANGO analyze-weight-tool is part of the SONATA powered by 5GTANGO Service Development Kit (SDK). The current repository contains a python based application which uses data analysis libraries in order to analyze the performance metrics of the chained Virtual Network Functions (VNFs) in a Network Service (NS). Starting an offline learning proccess with data gathered from the performance tests of a NS or even from the production environment, it calculates and stores the dependencies between the monitoring metrics of VNFs in a NoSQL database. Then, providing rest APIs as well as a GUI, the end user can request and get those dependencies of his/her VNF, thus getting an inside knowledge of the NS's performance behaviour. Among others, the end user can also request dependencies of a list of VNFs while the ones that are yet unknown to the tool are stored in another collection of the database. The goal of the aforementioned tool is to provide the test developer of 5GTANGO an inside knowledge of his/her NS, and thus, having those in mind develop more targeted tests.

##### Main Cababilities
*  Get a list of the supported-known VNFs
*  Get a list of the unsupported-unknown VNFs
*  Get dependencies of the VNFs in a NS (providing NS uuid existed in the tng-cat)
*  Get dependencies of an independed list of VNFs
*  Train for a new VNF (providing a .csv file with the VNF's performance-monitoring data)
*  Get correlation figure for a VNF (base64 format)

##### Example of a VNF's dependencies    

```json
[
  {
    "_id": "5c080fbe5700524338a500ec",
    "vnf": {
      "vnf_id": "vpn_vnf"
    },
    "correlations": [
      {
        "level_0": "end_to_end_latency",
        "level_1": "time_to_deploy_new_instance",
        "values": 0.9999978642
      },
      {
        "level_0": "number_of_streams",
        "level_1": "ping",
        "values": 0.9683217364
      },
      {
        "level_0": "cpu_usage",
        "level_1": "bandwidth",
        "values": 0.7045926301
      },
      {
        "level_0": "number_of_users",
        "level_1": "mem_usage",
        "values": 0.2736615039
      },
      {
        "level_0": "throughput",
        "level_1": "time_to_connect",
        "values": 0.235993478
      }
    ]
  }
]
```   

## Dependencies

### Programming Language
tng-sdk-analyze-weight has been programmed using Python 3.7. It mainly uses Flask microframework enabling interaction with it using rest APIs. Also part of the tool is a web application in html/css/js technologies providing a GUI to the end user. 

### Frameworks
*  Flask - Python Microframework

### Libraries
*  pandas : v0.23.4  (Apache 2.0)
*  matplotlib : v3.0.2 (Apache 2.0)
*  pymongo : 3.7.2 (Apache 2.0)
*  logmatic-python : 0.1.7 (Apache 2.0)

## Build and run tng-sdk-analyze-weight locally (Container mode using Docker)

```
git clone https://github.com/sonata-nfv/tng-sdk-analyze-weight
cd tng-sdk-analyze-weight
docker-compose up 
```

## Configuration

The following configurations are definied into the Dockerfile [here](https://github.com/sonata-nfv/tng-sdk-analyze-weight/blob/master/Dockerfile)
*  MongoDB 
    *  Specify database host
	*  Specify databse name
	*  Specify databse port

*  5GTANGO Catalogue - Specify the 5GTANGO Catalogue base url

### API References

We have specified this micro-service's API in a swagger-formated file. Please check it [here] (not implemented yet)

### Database

tng-sdk-analyze-weight tool is using [MongoDb](https://www.mongodb.com/) as database.  
The database includes the following collections:     
*  `dictionaries` - stores the weights-correlation for a vnf's metrics.
*  `unknown_vnfs` - stores the vnfs that acurrently the tool is not trained to give a response.
*  `encoded_figs` - stores a correlation figure in base64 format for each known vnf type

### Logging 

`tng-sdk-analyze-weight` uses the [logmatic-python 0.1.7](https://pypi.org/project/logmatic-python/) logging services, to produce logs in the 5GTANGO JSON format as described [here](https://git.cs.upb.de/5gtango/UserStories/issues/376) (authentication needed).       

```json
{
  "asctime": "2018-02-16T09:51:31Z",
  "name": "test", "processName": "MainProcess",
  "filename": "write_in_console.py",
  "funcName": "<module>",
  "levelname": "INFO",
  "lineno": 20,
  "module": "write_in_console",
  "threadName": "MainThread",
  "message": "classic message",
  "special": "value",
  "run": 12,
  "timestamp": "2016-02-16T09:51:31Z",
  "hostname": "<your_hostname>"
}
```     

### Contributing

You may contribute to the tng-sdk-analyze-weight tool you should:

1. Fork [this repository](https://github.com/sonata-nfv/tng-sdk-analyze-weight);
2. Work on your proposed changes, preferably through submiting [issues](https://github.com/sonata-nfv/tng-sdk-analyze-weight/issues);
3. Push changes on your fork;
3. Submit a Pull Request;
4. Follow/answer related [issues](https://github.com/sonata-nfv/tng-sdk-analyze-weight/issues) (see Feedback-Chanel, below).

### CI Integration

All pull requests are automatically tested by Jenkins and will only be accepted if no test is broken.


## License
tng-sdk-analyze-weight is published under Apache 2.0 license. Please see the LICENSE file [here](https://github.com/sonata-nfv/tng-sdk-analysis-weight/blob/master/LICENSE) for more details.

## Lead Developers

The following lead developers are responsible for this repository and have admin rights. They can, for example, merge pull requests.
*  Marios Touloupou (@mtouloup)
*  Evgenia Kapassa (@ekapassa)
  
## Feedback-Chanel
* GitHub issues