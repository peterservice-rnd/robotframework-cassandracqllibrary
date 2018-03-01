RobotFramework CassandraCQL Library
===================================

|Build Status|

Short Description
-----------------

`Robot Framework`_ library to execute CQL statements in Cassandra
Database.

Installation
------------

::

    pip install robotframework-cassandracqllibrary

Documentation
-------------

See keyword documentation for CassandraCQLLibrary library on `GitHub`_.

Example
-------

.. code:: robotframework

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
-------

Apache License 2.0

.. _Robot Framework: http://www.robotframework.org
.. _GitHub: https://github.com/peterservice-rnd/robotframework-cassandracqllibrary/tree/master/docs

.. |Build Status| image:: https://travis-ci.org/peterservice-rnd/robotframework-cassandracqllibrary.svg?branch=master
   :target: https://travis-ci.org/peterservice-rnd/robotframework-cassandracqllibrary
