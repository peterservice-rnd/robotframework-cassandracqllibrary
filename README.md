# RobotFramework CassandraCQL Library

[![Build Status](https://travis-ci.org/peterservice-rnd/robotframework-cassandracqllibrary.svg?branch=master)](https://travis-ci.org/peterservice-rnd/robotframework-cassandracqllibrary)

Short Description
---

[Robot Framework](http://www.robotframework.org) library to execute CQL statements in Cassandra Database.

Installation
---

```
pip install robotframework-cassandracqllibrary
```

Example
---

Example command to run test using pabot with report portal listener.
 
    *** Settings ***
    Library           CassandraCQLLibrary
    Library           Collections
    Suite Setup       Connect To Cassandra    127.0.0.1    9042
    Suite Teardown    Disconnect From Cassandra
    
    *** Test Cases ***
    Get Keyspaces
        Execute CQL    USE system
        ${result}    Execute CQL    SELECT * FROM schema_keyspaces;
        Log List    ${result}
        Log    ${result[1].keyspace_name}

License
---

Apache License 2.0
