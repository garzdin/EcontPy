import http
from re import match

ECONT_DEMO_URL = "http://demo.econt.com/e-econt/xml_parcel_import.php"
ECONT_DEMO_SERVICE_URL = "http://demo.econt.com/e-econt/xml_service_tool.php"
ECONT_URL = "http://www.econt.com/e-econt/xml_parcel_import.php"
ECONT_SERVICE_URL = "http://www.econt.com/e-econt/xml_service_tool.php"

REQUEST_SHIPMENTS = 0
REQUEST_CITIES_ZONES = 1
REQUEST_CITIES = 2
REQUEST_CITIES_REGIONS = 3
REQUEST_CITIES_STREETS = 4
REQUEST_CITIES_QUARTERS = 5
REQUEST_OFFICES = 6
REQUEST_POST_BOXES = 7
REQUEST_TARIFF_COURIER = 8
REQUEST_TARIFF_POST = 9
REQUEST_PROFILE = 10
REQUEST_REGISTRATION_REQUEST = 11
REQUEST_COUNTRIES = 12
REQUEST_CANCEL_SHIPMENTS = 13
REQUEST_DELIVERY_DAYS = 14
REQUEST_ACCOUNT_ROLES = 15
REQUEST_CLIENT_INFO = 16
REQUEST_ACCESS_CLIENTS = 17
REQUEST_CHECK_CD_AGREEMENT = 18
REQUEST_MEDIATOR_DATA = 19

REQUEST_TYPES = (
    (REQUEST_SHIPMENTS, 'shipments'), (REQUEST_CITIES_ZONES, 'cities_zones'),
    (REQUEST_CITIES, 'cities'), (REQUEST_CITIES_REGIONS, 'cities_regions'),
    (REQUEST_CITIES_STREETS, 'cities_streets'),
    (REQUEST_CITIES_QUARTERS, 'cities_quarters'), (REQUEST_OFFICES, 'offices'),
    (REQUEST_POST_BOXES, 'post_boxes'),
    (REQUEST_TARIFF_COURIER, 'tariff_courier'),
    (REQUEST_TARIFF_POST, 'tariff_post'), (REQUEST_PROFILE, 'profile'),
    (REQUEST_REGISTRATION_REQUEST, 'registration_request'),
    (REQUEST_COUNTRIES, 'countries'),
    (REQUEST_CANCEL_SHIPMENTS, 'cancel_shipments'),
    (REQUEST_DELIVERY_DAYS, 'delivery_days'),
    (REQUEST_ACCOUNT_ROLES, 'account_roles'),
    (REQUEST_CLIENT_INFO, 'client_info'),
    (REQUEST_ACCESS_CLIENTS, 'access_clients'),
    (REQUEST_CHECK_CD_AGREEMENT, 'check_cd_agreement'),
    (REQUEST_MEDIATOR_DATA, 'mediator_data')
)

TEMPLATE = "\
<?xml version=\"1.0\" encoding=\"UTF-8\"?> \
<request> \
    <client> \
        <username>{username}</username> \
        <password>{password}</password> \
    </client> \
    <request_type>{request_type}</request_type> \
    <updated_time>{updated_time}</updated_time> \
    {data} \
    <client_software>{client_software}</client_software> \
</request>"

DATE_FORMAT = r"[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])$"
UPDATED_TIME_FORMAT = r"[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])\s(0[1-9]|1[0-9]|2[0-4]):([1-5]?[0-9]|60):([1-5]?[0-9]|60)$"


class Client(object):
    def __init__(self, demo=False):
        self.username = None
        self.password = None
        self.demo = demo

    def login(self, username, password):
        self.username = username
        self.password = password
        return self

    def request(self,
                request_type=None,
                data=None,
                updated_time=None,
                client_software="EcontPy"):

        if not any(request_type in type_row for type_row in REQUEST_TYPES):
            raise Exception("Invalid request type")

        constructed_data = TEMPLATE.format(
            username=self.username,
            password=self.password,
            request_type=self.get_request_type(request_type),
            updated_time=updated_time if updated_time else "",
            data=data if data else "",
            client_software=client_software)

        return http.Request(ECONT_DEMO_SERVICE_URL
                                if self.demo else ECONT_SERVICE_URL).send(constructed_data)

    def get_request_type(self, type_id=None):
        return dict(REQUEST_TYPES)[type_id]

    def get_shipments(self, shipments=None, detailed=False):
        """
        Get shipments with the supplied tracking id(s)
        # Parameters
            * shipments [int/string/array] - array of shipments id(s)
            * full [bool] - whether to display information about the movement of the package
        """
        if not shipments:
            raise Exception("Invalid shipment id(s)")

        numbers = []

        if isinstance(shipments, int) or isinstance(shipments, str):
            numbers = [str(shipments)]
        else:
            for shipment in shipments:
                numbers.append("<num>{number}</num>".format(number=shipment))

        template = "<shipments full_tracking='{detailed}'>{data}</shipments>"
        data = template.format(detailed="ON" if detailed else "", data="".join(numbers))

        return self.request(REQUEST_SHIPMENTS, data)

    def get_cities_zones(self, updated_time=None):
        """
        Get zone information within cities
        # Parameters
            * updated_time [string] (optional) - The date from which to display entries
        """
        if updated_time:
            if not match(UPDATED_TIME_FORMAT, updated_time):
                raise Exception("Invalid date supplied")

            return self.request(REQUEST_CITIES_ZONES, None, updated_time)

        return self.request(REQUEST_CITIES_ZONES)

    def get_cities(self, cities=None, zone_id="all", report_type=None, updated_time=None):
        """
        Get cities (if at least one city is supplied it will do a search,
        otherwise it would return all cities)
        # Parameters
            * cities [array] - array of city names in cyrillic
            * zone_id [int/string] - a zone to constrain the search (See get_cities_zones())
            * report_type [string] - whether to display full information for a city or pass in 'short' for a shorter version
            * updated_time [string] (optional) - The date from which to display entries
        """
        if cities:
            city_names = []

            for city in cities:
                city_names.append("<city_name>{name}</city_name>".format(name=city))

            template = "<cities><report_type>{report_type}</report_type><id_zone>{zone_id}</id_zone>{data}</cities>"
            data = template.format(report_type=report_type, zone_id=zone_id, data="".join(city_names))

            if updated_time:
                if not match(UPDATED_TIME_FORMAT, updated_time):
                    raise Exception("Invalid date supplied")

                return self.request(REQUEST_CITIES, data, updated_time)

            return self.request(REQUEST_CITIES, data)

        if updated_time:
            if not match(UPDATED_TIME_FORMAT, updated_time):
                raise Exception("Invalid date supplied")

            return self.request(REQUEST_CITIES, None, updated_time)

        return self.request(REQUEST_CITIES)

    def get_cities_regions(self, updated_time=None):
        """
        Get region information within cities
        # Parameters
            * updated_time [string] (optional) - The date from which to display entries
        """
        if updated_time:
            if not match(UPDATED_TIME_FORMAT, updated_time):
                raise Exception("Invalid date supplied")

            return self.request(REQUEST_CITIES_REGIONS, None, updated_time)

        return self.request(REQUEST_CITIES_REGIONS)

    def get_cities_streets(self, updated_time=None):
        """
        Get street information within cities
        # Parameters
            * updated_time [string] (optional) - The date from which to display entries
        """
        if updated_time:
            if not match(UPDATED_TIME_FORMAT, updated_time):
                raise Exception("Invalid date supplied")

            return self.request(REQUEST_CITIES_STREETS, None, updated_time)

        return self.request(REQUEST_CITIES_STREETS)

    def get_cities_quarters(self, updated_time=None):
        """
        Get quarter information within cities
        # Parameters
            * updated_time [string] (optional) - The date from which to display entries
        """
        if updated_time:
            if not match(UPDATED_TIME_FORMAT, updated_time):
                raise Exception("Invalid date supplied")

            return self.request(REQUEST_CITIES_QUARTERS, None, updated_time)

        return self.request(REQUEST_CITIES_QUARTERS)

    def get_offices(self, updated_time=None):
        """
        Get offices information
        # Parameters
            * updated_time [string] (optional) - The date from which to display entries
        """
        if updated_time:
            if not match(UPDATED_TIME_FORMAT, updated_time):
                raise Exception("Invalid date supplied")

            return self.request(REQUEST_OFFICES, None, updated_time)

        return self.request(REQUEST_OFFICES)

    def get_post_boxes(self, locations=None):
        """
        Get post boxes information
        # Parameters
            * locations [array] - array of tuples in the form of (city_name, quarter_name)
        """
        if locations:
            locations_data = []

            for location in location:
                locations_data.append("<e><city_name>{city_name}</city_name><quarter_name>{quarter_name}</quarter_name></e>".format(city_name=location[0], quarter_name=location[1]))

            template = "<post_boxes>{data}</post_boxes>"
            data = template.format(data="".join(locations_data))

            return self.request(REQUEST_POST_BOXES, data)

        return self.request(REQUEST_POST_BOXES)

    def get_tariff_courier(self):
        """
        Get courier tariff information
        """
        return self.request(REQUEST_TARIFF_COURIER)

    def get_tariff_post(self):
        """
        Get post tariff information
        """
        return self.request(REQUEST_TARIFF_POST)

    def get_profile(self):
        """
        Get profile information
        """
        return self.request(REQUEST_PROFILE)

    def get_registraion_request(self, email=None):
        """
        Get registration requests information
        """
        if email:
            template = "<registration_request_mail>{data}</registration_request_mail>"
            data = template.format(data=email)

            return self.request(REQUEST_REGISTRATION_REQUEST, data)

        return self.request(REQUEST_REGISTRATION_REQUEST)

    def get_countries(self):
        """
        Get countries information
        """
        return self.request(REQUEST_COUNTRIES)

    def cancel_shipments(self, shipments=None):
        """
        Cancel shipments with the supplied ids
        # Parameters
            * shipments [array] - array of shipments ids
        """
        if not shipments:
            raise Exception("Invalid shipment id(s) supplied")

        numbers = []

        for shipment in shipments:
            numbers.append("<num>{number}</num>".format(number=shipment))

        template = "<cancel_shipments>{data}</cancel_shipments>"
        data = template.format(data="".join(numbers))

        return self.request(REQUEST_CANCEL_SHIPMENTS, data)

    def get_delivery_days(self, date=None):
        """
        Get available shipping days based on the current date
        """
        if not date:
            raise Exception("Invalid date supplied")

        if not match(DATE_FORMAT, date):
            raise Exception("Invalid date supplied")

        template = "<delivery_days>{data}</delivery_days>"
        data = template.format(data=date)

        return self.request(REQUEST_DELIVERY_DAYS, data)

    def get_client_info(self, ein=None, egn=None, client_id=None):
        """
        Get information about a client
        # Parameters
            * ein [int/string] - the EIN of the client
            * egn [int/string] - The EGN of the client
            * id [int/string] - The ID of the client
        """
        if not ein or not egn or not client_id:
            raise Exception("Invalid client information")

        template = "<ein>{ein}</ein><egn>{egn}</egn><id>{id}</id>"
        data = template.format(ein=ein, egn=egn, id=client_id)

        return self.request(REQUEST_CLIENT_INFO, data)

    def get_clients(self):
        """
        Get information about the clients of the current user
        """
        return self.request(REQUEST_ACCESS_CLIENTS)

    def check_cd_agreement(self, client_name=None, cd_agreement_id=None):
        """
        Verify the cash on delivery information
        # Parameters
            * client_name [string] - The name of the client
            * cd_agreement_id [int/string] - The id of the cash delivery agreement
        """
        if not client_name or not cd_agreement_id:
            raise Exception("Invalid Cash on Delivery information")

        template = "<client_name>{client_name}</client_name><cd_agreement>{cd_agreement_id}</cd_agreement>"
        data = template.format(client_name=client_name, cd_agreement_id=cd_agreement_id)

        return self.request(REQUEST_CHECK_CD_AGREEMENT, data)

    def get_mediator_data(self, mediator_id=None, from_date=None):
        """
        Get mediator information
        # Parameters
            * mediator_id [int/string] - The id of the mediator
            * from_date [string] (optional) - The date agains which to check
        """
        if not mediator_id:
            raise Exception("No mediator id supplied")

        template = "<mediator>{mediator}</mediator>"
        data = data = template.format(mediator=mediator_id)

        if from_date:
            if not match(DATE_FORMAT, from_date):
                raise Exception("Invalid date supplied")

            template = "<mediator>{mediator}</mediator><from_date>{from_date}</from_date>"
            data = template.format(mediator=mediator_id, from_date=from_date)

        return self.request(REQUEST_MEDIATOR_DATA, data)
