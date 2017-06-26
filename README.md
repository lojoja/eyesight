eyesight
========

Simple program to enable/disable the built-in iSight camera in macOS.


Requirements
------------

* macOS 10.10.x+
* Python 2.7.x
* System Integrity Protection must be [disabled](https://developer.apple.com/library/content/documentation/Security/Conceptual/System_Integrity_Protection_Guide/ConfiguringSystemIntegrityProtection/ConfiguringSystemIntegrityProtection.html)


Installation
------------

### Homebrew

```
$ brew tap lojoja/main
$ brew install eyesight
```

### Git

```
$ git clone https://github.com/lojoja/eyesight.git eyesight
$ cd eyesight
$ python setup.py install
```


Use
---

### Basic

Enable the camera:

```
$ sudo eyesight --enable
```

Disable the camera:

```
$ sudo eyesight --disable
```

Verbose:

```
$ sudo eyesight --disable --verbose
```

Quiet:

```
$ sudo eyesight --disable --quiet
```

### Brew Services

eyesight provides a `brew services` integration when installed via [Homebrew](https://brew.sh). This will automatically disable the camera
every time the system boots guarding against e.g., OS upgrades that re-enable it. To start the service run:

```
$ sudo brew services start eyesight
```


License
-------

eyesight is released under the [MIT License](./LICENSE)
