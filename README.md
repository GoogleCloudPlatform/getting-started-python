This is a fork from [GCPTraining bookshelf app](https://github.com/GoogleCloudPlatformTraining/cp100-bookshelf)

The following changes were made to fix two errors when deploying the Bookshelf application.

1. ImportError: cannot import name SpooledTemporaryFile
   fix: added line 8&9 to [cp100-bookshelf/app-engine/appengine_config.py](https://github.com/Flora7/cp100-bookshelf/blob/master/app-engine/appengine_config.py)
2. TemporaryFile() got an unexpected keyword argument 'max_size'
   fix: added file [cp100-bookshelf/cloud-storage/tempfile2.py](https://github.com/Flora7/cp100-bookshelf/blob/master/cloud-storage/tempfile2.py) and added line 8-10 to [cp100-bookshelf/cloud-storage/appengine_config.py](https://github.com/Flora7/cp100-bookshelf/blob/master/cloud-storage/appengine_config.py).

# cp100A-bookshelf-python
Used in the CP100A course - Collected sample code for the Bookshelf application.

## Contributing changes

* See [CONTRIBUTING.md](CONTRIBUTING.md)


## Licensing

* See [LICENSE](LICENSE)
