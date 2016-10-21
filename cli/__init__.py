# coding=utf-8
from re import match
from json import loads, dumps
from requests import post
from xmltodict import parse

ECONT_DEMO_URL = "http://demo.econt.com/e-econt/xml_parcel_import.php"
ECONT_DEMO_SERVICE_URL = "http://demo.econt.com/e-econt/xml_service_tool.php"
ECONT_URL = "http://www.econt.com/e-econt/xml_parcel_import.php"
ECONT_SERVICE_URL = "http://www.econt.com/e-econt/xml_service_tool.php"

REQUEST_SHIPMENTS = 1
REQUEST_CITIES_ZONES = 2
REQUEST_CITIES = 3
REQUEST_CITIES_REGIONS = 4
REQUEST_CITIES_STREETS = 5
REQUEST_CITIES_QUARTERS = 6
REQUEST_OFFICES = 7
REQUEST_POST_BOXES = 8
REQUEST_TARIFF_COURIER = 9
REQUEST_TARIFF_POST = 10
REQUEST_PROFILE = 11
REQUEST_REGISTRATION_REQUEST = 12
REQUEST_COUNTRIES = 13
REQUEST_CANCEL_SHIPMENTS = 14
REQUEST_DELIVERY_DAYS = 15
REQUEST_ACCOUNT_ROLES = 16
REQUEST_CLIENT_INFO = 17
REQUEST_ACCESS_CLIENTS = 18
REQUEST_CHECK_CD_AGREEMENT = 19
REQUEST_MEDIATOR_DATA = 20
REQUEST_CHECK_ADDRESS = 21

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
    (REQUEST_MEDIATOR_DATA, 'mediator_data'),
    (REQUEST_CHECK_ADDRESS, 'check_address')
)

TEMPLATE = "\
<?xml version=\"1.0\" encoding=\"UTF-8\"?>\
<request>\
    <client>\
        <username>{username}</username>\
        <password>{password}</password>\
    </client>\
    <request_type>{request_type}</request_type>\
    <updated_time>{updated_time}</updated_time>\
    {data}\
    <client_software>{client_software}</client_software>\
</request>"

DATE_FORMAT = r"[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])$"
UPDATED_TIME_FORMAT = r"[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])\s(0[1-9]|1[0-9]|2[0-4]):([1-5]?[0-9]|60):([1-5]?[0-9]|60)$"


class Client(object):
    def __init__(self, username=None, password=None, demo=False):
        """Instantiate the client object

        Keyword args:
        [string] username -- the econt.bg username for the account
        [string] password -- the econt.bg password for the account
        [bool] demo -- whether we're running in demo mode or not (default False)
        """
        if not username or not password:
            raise Exception("No username or password supplied")

        self.username = username
        self.password = password
        self.demo = demo

    def request(self,
                request_type=None,
                data=None,
                updated_time=None,
                client_software="EcontPy"):
        """Build and send a request with the given Parameters

        Keyword args:
        [int] request_type -- the type of the request from REQUEST_TYPES (default None)
        [string] data -- the data to be sent with the request (default None)
        [string] updated_time (optional) -- the time from which to return data (default None)
        [string] client_software -- the name of the client, that is sending data (Default 'EcontPy')
        """

        if not any(request_type in type_row for type_row in REQUEST_TYPES):
            raise Exception("Invalid request type")

        constructed_data = TEMPLATE.format(
            username=self.username,
            password=self.password,
            request_type=self.get_request_type(request_type),
            updated_time=updated_time if updated_time else "",
            data=data if data else "",
            client_software=client_software)

        response = post(
            ECONT_DEMO_SERVICE_URL if self.demo else ECONT_SERVICE_URL,
            files={'file': constructed_data}
        )

        return loads(dumps(parse(response.text.encode('utf-8'))))

    def get_request_type(self, type_id=None):
        """Get the request type from REQUEST_TYPES by id

        Keyword args:
        [int] type_id -- the type id from REQUEST_TYPES (default None)
        """
        if not type_id:
            raise Exception("No type id supplied")

        return dict(REQUEST_TYPES)[type_id]

    def get_shipments(self, shipments=None, detailed=False):
        """Get shipments with the supplied tracking id(s)

        Keyword args:
        [int/string/array] shipments -- array of shipments id(s) (default None)
        [bool] detailed - whether to display information about the movement of the package (default False)
        """
        if not shipments:
            raise Exception("Invalid shipment id(s)")

        numbers = []

        if isinstance(shipments, (int, str)):
            numbers = [str(shipments)]
        else:
            for shipment in shipments:
                numbers.append("<num>{number}</num>".format(number=shipment))

        template = "<shipments full_tracking='{detailed}'>{data}</shipments>"
        data = template.format(detailed="ON" if detailed else "", data="".join(numbers))

        return self.request(REQUEST_SHIPMENTS, data)

    def validate_address(self, city=None, post_code=None, quarter=None, street=None, street_num=None,
                     building=None, entrance=None, floor=None, apartment=None, other=None, email=None):
        """Check if an address is valid

        Keyword args:
        [string] city -- the name of the city (default None)
        [int/string] post_code (optional) -- the post code of the city (default None)
        [string] quarter (optional) -- the name of the quarter (default None)
        [string] street (optional) -- the name of the street (default None)
        [int/string] street_num (optional) -- the number of the street (default None)
        [string] building (optional) -- the name of the building (default None)
        [string] entrance (optional) -- the entrance name for a building (default None)
        [int/string] floor (optional) -- the floor in the building (default None)
        [int/string] apartment (optional) -- the number of the apartment (default None)
        [string] other (optional) -- other data
        [string] email (optional) -- an email to which to send information about a shipment on this address
        """
        if not city:
            raise Exception("Invalid city supplied")

        template = "<address>\
                        <city>{city}</city>\
                        <post_code>{post_code}</post_code>\
                        <quarter>{quarter}</quarter>\
                        <street>{street}</street>\
                        <street_num>{street_num}</street_num>\
                        <street_bl>{building}</street_bl>\
                        <street_vh>{entrance}</street_vh>\
                        <street_et>{floor}</street_et>\
                        <street_ap>{apartment}</street_ap>\
                        <street_other>{other}</street_other>\
                        <email_on_delivery>{email}</email_on_delivery>\
                    </address>"
        data = template.format(
                    city=city,
                    post_code=post_code,
                    quarter=quarter, street=street,
                    street_num=street_num,
                    building=building,
                    entrance=entrance,
                    floor=floor,
                    apartment=apartment,
                    other=other,
                    email=email
                )

        return self.request(REQUEST_CHECK_ADDRESS, data)


    def get_cities_zones(self, updated_time=None):
        """Get zone information within cities

        Keyword args:
        [string] updated_time (optional) -- the date from which to display entries (default None)
        """
        if updated_time:
            if not match(UPDATED_TIME_FORMAT, updated_time):
                raise Exception("Invalid date supplied")

            return self.request(REQUEST_CITIES_ZONES, None, updated_time)

        return self.request(REQUEST_CITIES_ZONES)

    def get_cities(self, cities=None, zone_id="all", report_type=None, updated_time=None):
        """Get cities (if at least one city is supplied it will do a search,
        otherwise it would return all cities)

        Keyword args:
        [array] cities -- array of city names in cyrillic (default None)
        [int/string] zone_id -- a zone to constrain the search to (default 'all')
        [string] report_type -- whether to display full information for a city or pass in 'short' for a shorter version (default None)
        [string] updated_time (optional) -- the date from which to display entries (default None)
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
        """Get region information within cities
        Keyword args:
        [string] updated_time (optional) -- the date from which to display entries (default None)
        """
        if updated_time:
            if not match(UPDATED_TIME_FORMAT, updated_time):
                raise Exception("Invalid date supplied")

            return self.request(REQUEST_CITIES_REGIONS, None, updated_time)

        return self.request(REQUEST_CITIES_REGIONS)

    def get_cities_streets(self, updated_time=None):
        """Get street information within cities

        Keyword args:
        [string] updated_time (optional) -- the date from which to display entries (default None)
        """
        if updated_time:
            if not match(UPDATED_TIME_FORMAT, updated_time):
                raise Exception("Invalid date supplied")

            return self.request(REQUEST_CITIES_STREETS, None, updated_time)

        return self.request(REQUEST_CITIES_STREETS)

    def get_cities_quarters(self, updated_time=None):
        """Get quarter information within cities

        Keyword args:
        [string] updated_time (optional) -- the date from which to display entries (default None)
        """
        if updated_time:
            if not match(UPDATED_TIME_FORMAT, updated_time):
                raise Exception("Invalid date supplied")

            return self.request(REQUEST_CITIES_QUARTERS, None, updated_time)

        return self.request(REQUEST_CITIES_QUARTERS)

    def get_offices(self, updated_time=None):
        """Get offices information

        Keyword args:
        [string] updated_time (optional) -- the date from which to display entries (default None)
        """
        if updated_time:
            if not match(UPDATED_TIME_FORMAT, updated_time):
                raise Exception("Invalid date supplied")

            return self.request(REQUEST_OFFICES, None, updated_time)

        return self.request(REQUEST_OFFICES)

    def get_post_boxes(self, locations=None):
        """Get post boxes information

        Keyword args:
        [array] locations (optional) -- array of tuples in the form of (city_name, quarter_name)
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
        """Get courier tariff information"""
        return self.request(REQUEST_TARIFF_COURIER)

    def get_tariff_post(self):
        """Get post tariff information"""
        return self.request(REQUEST_TARIFF_POST)

    def get_profile(self):
        """Get profile information"""
        return self.request(REQUEST_PROFILE)

    def get_registraion_request(self, email=None):
        """Get registration requests information

        Keyword args:
        [string] email (optional) -- the email for which to get information about the request
        """
        if email:
            template = "<registration_request_mail>{data}</registration_request_mail>"
            data = template.format(data=email)

            return self.request(REQUEST_REGISTRATION_REQUEST, data)

        return self.request(REQUEST_REGISTRATION_REQUEST)

    def get_countries(self):
        """Get countries information"""
        return self.request(REQUEST_COUNTRIES)

    def cancel_shipments(self, shipments=None):
        """Cancel shipments with the supplied ids

        Keyword args:
        [array] shipments -- array of shipments ids
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
        """Get available shipping days based on a given date

        Keyword args:
        [string] date -- the date from which to check (default None)
        """
        if not date:
            raise Exception("Invalid date supplied")

        if not match(DATE_FORMAT, date):
            raise Exception("Invalid date supplied")

        template = "<delivery_days>{data}</delivery_days>"
        data = template.format(data=date)

        return self.request(REQUEST_DELIVERY_DAYS, data)

    def get_client_info(self, ein=None, egn=None, client_id=None):
        """Get information about a client

        Keyword args:
        [int/string] ein - the EIN of the client
        [int/string] egn - the EGN of the client
        [int/string] id - the ID of the client
        """
        if not ein or not egn or not client_id:
            raise Exception("Invalid client information")

        template = "<ein>{ein}</ein><egn>{egn}</egn><id>{id}</id>"
        data = template.format(ein=ein, egn=egn, id=client_id)

        return self.request(REQUEST_CLIENT_INFO, data)

    def get_clients(self):
        """Get information about the clients of the current user"""
        return self.request(REQUEST_ACCESS_CLIENTS)

    def check_cd_agreement(self, client_name=None, cd_agreement_id=None):
        """Verify the cash on delivery information

        Keyword args:
        [string] client_name - the name of the client (default None)
        [int/string] cd_agreement_id - the id of the cash delivery agreement (default None)
        """
        if not client_name or not cd_agreement_id:
            raise Exception("Invalid Cash on Delivery information")

        template = "<client_name>{client_name}</client_name><cd_agreement>{cd_agreement_id}</cd_agreement>"
        data = template.format(client_name=client_name, cd_agreement_id=cd_agreement_id)

        return self.request(REQUEST_CHECK_CD_AGREEMENT, data)

    def get_mediator_data(self, mediator_id=None, from_date=None):
        """Get mediator information

        Keyword args:
        [int/string] mediator_id - the id of the mediator (default None)
        [string] from_date (optional) - the date agains which to check (default None)
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

if __name__ == '__main__':
    c = Client("iasp-dev", "iasp-dev", True)
    print(c.get_shipments([1234, 12345]))
