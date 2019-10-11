# -*- coding: utf-8 -*-

from typing import List, Optional, Union

from robot.api import logger
from robot.utils import ConnectionCache
from cassandra.auth import PlainTextAuthProvider
from cassandra.policies import TokenAwarePolicy, DCAwareRoundRobinPolicy
from cassandra.cluster import Cluster, ResponseFuture, ResultSet, Session


class CassandraCQLLibrary(object):
    """
    Library for executing CQL statements in database [ http://cassandra.apache.org/ | Apache Cassandra ].

    == Dependencies ==
    | datastax python-driver | https://github.com/datastax/python-driver |
    | robot framework | http://robotframework.org |

    == Additional Information ==
    - [ http://www.datastax.com/documentation/cql/3.1/cql/cql_using/about_cql_c.html | CQL query language]

    == Example ==
    | *Settings* | *Value* | *Value* | *Value* |
    | Library    | CassandraCQLLibrary |
    | Library    | Collections |
    | Suite Setup     |  Connect To Cassandra  |  192.168.33.10  |  9042 |
    | Suite Teardown  |  Disconnect From Cassandra |

    | *Test Cases*  | *Action* | *Argument* | *Argument* |
    | Get Keyspaces |
    |               | Execute CQL  |  USE system |
    |               | ${result}=   |  Execute CQL  |  SELECT * FROM schema_keyspaces; |
    |               | Log List  |  ${result} |
    |               | Log  |  ${result[1].keyspace_name} |
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self) -> None:
        """ Initialization. """
        self._connection: Optional[Session] = None
        self._cache = ConnectionCache()

    @property
    def keyspace(self) -> str:
        """Get keyspace Cassandra.

        Returns:
            keyspace: the name of the keyspace in Cassandra.
        """
        if self._connection is None:
            raise Exception('There is no connection to Cassandra cluster.')
        return self._connection.keyspace

    def connect_to_cassandra(self, host: str, port: Union[int, str] = 9042, alias: str = None, keyspace: str = None,
                             username: str = None, password: str = '') -> Session:
        """
        Connect to Apache Cassandra cluster.

        AllowAllAuthenticator and PasswordAuthenticator are supported as authentication backend.
        This setting should be in configuration file cassandra.yaml:
        by default:
        | authenticator: AllowAllAuthenticator
        or for password authentification:
        | authenticator: PasswordAuthenticator

        *Args:*\n
            _host_ - IP address or host name of a cluster node;\n
            _port_ - connection port;\n
            _alias_ - connection alias;\n
            _keyspace_ - the name of the keyspace that the UDT is defined in;\n
            _username_ - username to connect to cassandra
            _password_ - password for username

        *Returns:*\n
            Index of current connection.

        *Example:*\n
        | Connect To Cassandra  |  192.168.1.108  |  9042  |  alias=cluster1 |
        """

        logger.info('Connecting using : host={0}, port={1}, alias={2}'.format(host, port, alias))
        try:
            auth_provider = PlainTextAuthProvider(username=username, password=password) if username else None
            cluster = Cluster([host], port=int(port), auth_provider=auth_provider,
                              load_balancing_policy=TokenAwarePolicy(DCAwareRoundRobinPolicy()))

            session = cluster.connect()
            if keyspace is not None:
                session.set_keyspace(keyspace)
            self._connection = session
            return self._cache.register(self._connection, alias)
        except Exception as e:
            raise Exception('Connect to Cassandra error: {0}'.format(e))

    def disconnect_from_cassandra(self) -> None:
        """
        Close current connection with cluster.

        *Example:*\n
        | Connect To Cassandra  |  server-host.local |
        | Disconnect From Cassandra |
        """
        if self._connection is None:
            raise Exception('There is no connection to Cassandra cluster.')
        self._connection.shutdown()

    def close_all_cassandra_connections(self) -> None:
        """
        Close all connections with cluster.

        This keyword is used to close all connections only in case if there are several open connections.
        Do not use keywords [#Disconnect From Cassandra|Disconnect From Cassandra] and
        [#Close All Cassandra Connections|Close All Cassandra Connections] together.

        After this keyword is executed, the index returned by [#Connect To Cassandra | Connect To Cassandra]
        starts at 1.

        *Example:*\n
        | Connect To Cassandra  |  192.168.1.108  | alias=cluster1 |
        | Connect To Cassandra  |  192.168.1.208  | alias=cluster2 |
        | Close All Cassandra Connections |
        """
        self._connection = self._cache.close_all(closer_method='shutdown')

    def switch_cassandra_connection(self, index_or_alias: Union[int, str]) -> int:
        """
        Switch between active connections with several clusters using their index or alias.

        Connection alias is set in keyword [#Connect To Cassandra|Connect To Cassandra],
        which also returns the index of connection.

        *Args:*\n
            _index_or_alias_ - connection index or alias;

        *Returns:*\n
            Index of the previous connection.

        *Example:* (switch by alias)\n
        | Connect To Cassandra  |  192.168.1.108  | alias=cluster1 |
        | Connect To Cassandra  |  192.168.1.208  | alias=cluster2 |
        | Switch Cassandra Connection  |  cluster1 |

        *Example:* (switch by index)\n
        | ${cluster1}=  |  Connect To Cassandra  |  192.168.1.108  |
        | ${cluster2}= | Connect To Cassandra  |  192.168.1.208  |
        | ${previous_index}=  |  Switch Cassandra Connection  |  ${cluster1} |
        | Switch Cassandra Connection  |  ${previous_index} |
        =>\n
        ${cluster1}= 1\n
        ${cluster2}= 2\n
        ${previous_index}= 2\n
        """
        old_index = self._cache.current_index
        self._connection = self._cache.switch(index_or_alias)
        return old_index

    def execute_cql(self, statement: str) -> ResultSet:
        """
        Execute CQL statement.

        *Args:*\n
            _statement_ - CQL statement;

        *Returns:*\n
            Execution result.

        *Example:*\n
        | ${result}=  |  Execute CQL  |  SELECT * FROM system.schema_keyspaces; |
        | Log  |  ${result[1].keyspace_name} |
        =>\n
        system
        """
        if not self._connection:
            raise Exception('There is no connection to Cassandra cluster.')

        logger.debug("Executing :\n %s" % statement)
        result = self._connection.execute(statement, timeout=60)
        return result

    def execute_async_cql(self, statement: str) -> ResponseFuture:
        """
        Execute asynchronous CQL statement.

        *Args:*\n
            _statement_ - CQL statement;

        *Returns:*\n
            Object that can be used with keyword [#Get Async Result | Get Async Result] to get the result of CQL statement.
        """
        if not self._connection:
            raise Exception('There is no connection to Cassandra cluster.')

        logger.debug("Executing :\n %s" % statement)
        future = self._connection.execute_async(statement)
        return future

    def get_async_result(self, future: ResponseFuture) -> ResultSet:
        """
        Get the result of asynchronous CQL statement.

        *Args:*\n
            _future_ - object, returned as a result of keyword [#Execute Async Cql | Execute Async Cql]

        *Returns:*\n
            Result of asynchronous CQL statement.

        *Example:*\n
        | ${obj}=  |  Execute Async Cql  |  SELECT * FROM system.schema_keyspaces; |
        | Sleep | 5 |
        | ${result}=  |  Get Async Result  |  ${obj} |
        | Log  |  ${result[1].keyspace_name} |
        =>\n
        system
        """
        try:
            result = future.result()
        except Exception as e:
            raise Exception('Operation failed: {0}'.format(e))
        return result

    def get_column(self, column: str, statement: str) -> List[str]:
        """
        Get column values from the data sampling.

        *Args:*\n
            _column_ - name of the column which value you want to get;\n
            _statement_ - CQL select statement.

        *Returns:*\n
            List of column values.

        *Example:*\n
        | ${result}=  |  Get Column  |  keyspace_name  |  SELECT * FROM system.schema_keyspaces LIMIT 2; |
        | Log List  |  ${result} |
        =>\n
        | List length is 2 and it contains following items:
        | 0: test
        | 1: OpsCenter
        """
        result = self.execute_cql(statement)
        result_values = []
        for item in result:
            column_attr = str(getattr(item, column))
            result_values.append(column_attr)
        return result_values

    def get_column_from_schema_keyspaces(self, column: str) -> List[str]:
        """Get column values from the table schema_keyspaces.

        *Args:*\n
            _column_ - the name of the column which values you want to get;\n

        *Returns:*\n
            List of column values from the table schema_keyspaces.
        """
        statement = """SELECT *
                       FROM system.schema_keyspaces"""

        return self.get_column(column, statement)
