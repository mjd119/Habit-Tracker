# coding=utf-8
"""
This code was generated by
\ / _    _  _|   _  _
 | (_)\/(_)(_|\/| |(/_  v1.0.0
      /       /
"""

from twilio.base import deserialize
from twilio.base import serialize
from twilio.base import values
from twilio.base.instance_context import InstanceContext
from twilio.base.instance_resource import InstanceResource
from twilio.base.list_resource import ListResource
from twilio.base.page import Page
from twilio.rest.studio.v1.flow.execution.execution_context import ExecutionContextList
from twilio.rest.studio.v1.flow.execution.execution_step import ExecutionStepList


class ExecutionList(ListResource):
    """  """

    def __init__(self, version, flow_sid):
        """
        Initialize the ExecutionList

        :param Version version: Version that contains the resource
        :param flow_sid: Flow Sid.

        :returns: twilio.rest.studio.v1.flow.execution.ExecutionList
        :rtype: twilio.rest.studio.v1.flow.execution.ExecutionList
        """
        super(ExecutionList, self).__init__(version)

        # Path Solution
        self._solution = {'flow_sid': flow_sid, }
        self._uri = '/Flows/{flow_sid}/Executions'.format(**self._solution)

    def stream(self, limit=None, page_size=None):
        """
        Streams ExecutionInstance records from the API as a generator stream.
        This operation lazily loads records as efficiently as possible until the limit
        is reached.
        The results are returned as a generator, so this operation is memory efficient.

        :param int limit: Upper limit for the number of records to return. stream()
                          guarantees to never return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, stream() will attempt to read the
                              limit with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.studio.v1.flow.execution.ExecutionInstance]
        """
        limits = self._version.read_limits(limit, page_size)

        page = self.page(page_size=limits['page_size'], )

        return self._version.stream(page, limits['limit'], limits['page_limit'])

    def list(self, limit=None, page_size=None):
        """
        Lists ExecutionInstance records from the API as a list.
        Unlike stream(), this operation is eager and will load `limit` records into
        memory before returning.

        :param int limit: Upper limit for the number of records to return. list() guarantees
                          never to return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, list() will attempt to read the limit
                              with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.studio.v1.flow.execution.ExecutionInstance]
        """
        return list(self.stream(limit=limit, page_size=page_size, ))

    def page(self, page_token=values.unset, page_number=values.unset,
             page_size=values.unset):
        """
        Retrieve a single page of ExecutionInstance records from the API.
        Request is executed immediately

        :param str page_token: PageToken provided by the API
        :param int page_number: Page Number, this value is simply for client state
        :param int page_size: Number of records to return, defaults to 50

        :returns: Page of ExecutionInstance
        :rtype: twilio.rest.studio.v1.flow.execution.ExecutionPage
        """
        params = values.of({'PageToken': page_token, 'Page': page_number, 'PageSize': page_size, })

        response = self._version.page(
            'GET',
            self._uri,
            params=params,
        )

        return ExecutionPage(self._version, response, self._solution)

    def get_page(self, target_url):
        """
        Retrieve a specific page of ExecutionInstance records from the API.
        Request is executed immediately

        :param str target_url: API-generated URL for the requested results page

        :returns: Page of ExecutionInstance
        :rtype: twilio.rest.studio.v1.flow.execution.ExecutionPage
        """
        response = self._version.domain.twilio.request(
            'GET',
            target_url,
        )

        return ExecutionPage(self._version, response, self._solution)

    def create(self, to, from_, parameters=values.unset):
        """
        Create a new ExecutionInstance

        :param unicode to: The Contact phone number to start a Studio Flow Execution.
        :param unicode from_: The Twilio phone number to send messages or initiate calls from during the Flow Execution.
        :param dict parameters: JSON data that will be added to your flow's context and can accessed as variables inside your flow.

        :returns: Newly created ExecutionInstance
        :rtype: twilio.rest.studio.v1.flow.execution.ExecutionInstance
        """
        data = values.of({'To': to, 'From': from_, 'Parameters': serialize.object(parameters), })

        payload = self._version.create(
            'POST',
            self._uri,
            data=data,
        )

        return ExecutionInstance(self._version, payload, flow_sid=self._solution['flow_sid'], )

    def get(self, sid):
        """
        Constructs a ExecutionContext

        :param sid: Execution Sid.

        :returns: twilio.rest.studio.v1.flow.execution.ExecutionContext
        :rtype: twilio.rest.studio.v1.flow.execution.ExecutionContext
        """
        return ExecutionContext(self._version, flow_sid=self._solution['flow_sid'], sid=sid, )

    def __call__(self, sid):
        """
        Constructs a ExecutionContext

        :param sid: Execution Sid.

        :returns: twilio.rest.studio.v1.flow.execution.ExecutionContext
        :rtype: twilio.rest.studio.v1.flow.execution.ExecutionContext
        """
        return ExecutionContext(self._version, flow_sid=self._solution['flow_sid'], sid=sid, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Studio.V1.ExecutionList>'


class ExecutionPage(Page):
    """  """

    def __init__(self, version, response, solution):
        """
        Initialize the ExecutionPage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API
        :param flow_sid: Flow Sid.

        :returns: twilio.rest.studio.v1.flow.execution.ExecutionPage
        :rtype: twilio.rest.studio.v1.flow.execution.ExecutionPage
        """
        super(ExecutionPage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of ExecutionInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.studio.v1.flow.execution.ExecutionInstance
        :rtype: twilio.rest.studio.v1.flow.execution.ExecutionInstance
        """
        return ExecutionInstance(self._version, payload, flow_sid=self._solution['flow_sid'], )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Studio.V1.ExecutionPage>'


class ExecutionContext(InstanceContext):
    """  """

    def __init__(self, version, flow_sid, sid):
        """
        Initialize the ExecutionContext

        :param Version version: Version that contains the resource
        :param flow_sid: Flow Sid.
        :param sid: Execution Sid.

        :returns: twilio.rest.studio.v1.flow.execution.ExecutionContext
        :rtype: twilio.rest.studio.v1.flow.execution.ExecutionContext
        """
        super(ExecutionContext, self).__init__(version)

        # Path Solution
        self._solution = {'flow_sid': flow_sid, 'sid': sid, }
        self._uri = '/Flows/{flow_sid}/Executions/{sid}'.format(**self._solution)

        # Dependents
        self._steps = None
        self._execution_context = None

    def fetch(self):
        """
        Fetch a ExecutionInstance

        :returns: Fetched ExecutionInstance
        :rtype: twilio.rest.studio.v1.flow.execution.ExecutionInstance
        """
        params = values.of({})

        payload = self._version.fetch(
            'GET',
            self._uri,
            params=params,
        )

        return ExecutionInstance(
            self._version,
            payload,
            flow_sid=self._solution['flow_sid'],
            sid=self._solution['sid'],
        )

    def delete(self):
        """
        Deletes the ExecutionInstance

        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        return self._version.delete('delete', self._uri)

    @property
    def steps(self):
        """
        Access the steps

        :returns: twilio.rest.studio.v1.flow.execution.execution_step.ExecutionStepList
        :rtype: twilio.rest.studio.v1.flow.execution.execution_step.ExecutionStepList
        """
        if self._steps is None:
            self._steps = ExecutionStepList(
                self._version,
                flow_sid=self._solution['flow_sid'],
                execution_sid=self._solution['sid'],
            )
        return self._steps

    @property
    def execution_context(self):
        """
        Access the execution_context

        :returns: twilio.rest.studio.v1.flow.execution.execution_context.ExecutionContextList
        :rtype: twilio.rest.studio.v1.flow.execution.execution_context.ExecutionContextList
        """
        if self._execution_context is None:
            self._execution_context = ExecutionContextList(
                self._version,
                flow_sid=self._solution['flow_sid'],
                execution_sid=self._solution['sid'],
            )
        return self._execution_context

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Studio.V1.ExecutionContext {}>'.format(context)


class ExecutionInstance(InstanceResource):
    """  """

    class Status(object):
        ACTIVE = "active"
        ENDED = "ended"

    def __init__(self, version, payload, flow_sid, sid=None):
        """
        Initialize the ExecutionInstance

        :returns: twilio.rest.studio.v1.flow.execution.ExecutionInstance
        :rtype: twilio.rest.studio.v1.flow.execution.ExecutionInstance
        """
        super(ExecutionInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'sid': payload['sid'],
            'account_sid': payload['account_sid'],
            'flow_sid': payload['flow_sid'],
            'contact_sid': payload['contact_sid'],
            'contact_channel_address': payload['contact_channel_address'],
            'context': payload['context'],
            'status': payload['status'],
            'date_created': deserialize.iso8601_datetime(payload['date_created']),
            'date_updated': deserialize.iso8601_datetime(payload['date_updated']),
            'url': payload['url'],
            'links': payload['links'],
        }

        # Context
        self._context = None
        self._solution = {'flow_sid': flow_sid, 'sid': sid or self._properties['sid'], }

    @property
    def _proxy(self):
        """
        Generate an instance context for the instance, the context is capable of
        performing various actions.  All instance actions are proxied to the context

        :returns: ExecutionContext for this ExecutionInstance
        :rtype: twilio.rest.studio.v1.flow.execution.ExecutionContext
        """
        if self._context is None:
            self._context = ExecutionContext(
                self._version,
                flow_sid=self._solution['flow_sid'],
                sid=self._solution['sid'],
            )
        return self._context

    @property
    def sid(self):
        """
        :returns: A string that uniquely identifies this Execution.
        :rtype: unicode
        """
        return self._properties['sid']

    @property
    def account_sid(self):
        """
        :returns: Account Sid.
        :rtype: unicode
        """
        return self._properties['account_sid']

    @property
    def flow_sid(self):
        """
        :returns: Flow Sid.
        :rtype: unicode
        """
        return self._properties['flow_sid']

    @property
    def contact_sid(self):
        """
        :returns: Contact Sid.
        :rtype: unicode
        """
        return self._properties['contact_sid']

    @property
    def contact_channel_address(self):
        """
        :returns: The phone number, SIP address or Client identifier that triggered this Execution.
        :rtype: unicode
        """
        return self._properties['contact_channel_address']

    @property
    def context(self):
        """
        :returns: The context
        :rtype: dict
        """
        return self._properties['context']

    @property
    def status(self):
        """
        :returns: The Status of this Execution
        :rtype: ExecutionInstance.Status
        """
        return self._properties['status']

    @property
    def date_created(self):
        """
        :returns: The date this Execution was created
        :rtype: datetime
        """
        return self._properties['date_created']

    @property
    def date_updated(self):
        """
        :returns: The date this Execution was updated
        :rtype: datetime
        """
        return self._properties['date_updated']

    @property
    def url(self):
        """
        :returns: The URL of this resource.
        :rtype: unicode
        """
        return self._properties['url']

    @property
    def links(self):
        """
        :returns: Nested resource URLs.
        :rtype: unicode
        """
        return self._properties['links']

    def fetch(self):
        """
        Fetch a ExecutionInstance

        :returns: Fetched ExecutionInstance
        :rtype: twilio.rest.studio.v1.flow.execution.ExecutionInstance
        """
        return self._proxy.fetch()

    def delete(self):
        """
        Deletes the ExecutionInstance

        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        return self._proxy.delete()

    @property
    def steps(self):
        """
        Access the steps

        :returns: twilio.rest.studio.v1.flow.execution.execution_step.ExecutionStepList
        :rtype: twilio.rest.studio.v1.flow.execution.execution_step.ExecutionStepList
        """
        return self._proxy.steps

    @property
    def execution_context(self):
        """
        Access the execution_context

        :returns: twilio.rest.studio.v1.flow.execution.execution_context.ExecutionContextList
        :rtype: twilio.rest.studio.v1.flow.execution.execution_context.ExecutionContextList
        """
        return self._proxy.execution_context

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Studio.V1.ExecutionInstance {}>'.format(context)
