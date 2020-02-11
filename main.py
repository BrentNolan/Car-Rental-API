#!/usr/bin/env python


from google.appengine.ext import ndb

import webapp2
import json

# The following 2 functions adapted from Convert NDB result to # JSON Serializable data
# https://gist.github.com/bengrunfeld/062d0d8360667c47bc5b


def make_ndb_return_data_json_serializable(data, urltype):
    # Build a new dict so that the data can be JSON serializable

    result = data.to_dict()
    record = {}

    # Populate the new dict with JSON serializiable values
    for key in result.iterkeys():
        record[key] = result[key]

    # Add self reference
    record['self'] = urltype + data.id

    return record


def filter_results(qry, urltype):
    """
    Send NDB query result to serialize function if single result, 
    else loop through the query result and serialize records one by one
    """

    result = []

    # check if qry is a list (multiple records) or not (single record)
    if type(qry) != list:
        record = make_ndb_return_data_json_serializable(qry, urltype)
        return record

    for q in qry:
        result.append(make_ndb_return_data_json_serializable(q, urltype))

    return result

# [START Data classes]

#class Address(ndb.Model):
#   street = ndb.StringProperty()
#   city = ndb.StringProperty()
#   state = ndb.StringProperty()
#   zip_code = ndb.IntegerProperty()

admin_id ='1/JWSERU4gfKie5XL-oHeotJlb1mODohPKYwsJTUKXsiI'


class Account(ndb.Model):
    id = ndb.StringProperty()
    name = ndb.StringProperty(required=True)
    address = ndb.StringProperty()
    phone_number = ndb.StringProperty()
    d_license = ndb.StringProperty()
    dl_state = ndb.StringProperty()
    auth = ndb.StringProperty()


class Car(ndb.Model):
    id = ndb.StringProperty()
    make = ndb.StringProperty()
    model = ndb.StringProperty()
    color = ndb.StringProperty()
    year = ndb.IntegerProperty()
    v_license = ndb.StringProperty()
    v_state = ndb.StringProperty()
    current_account = ndb.StringProperty()
    start_date = ndb.StringProperty()
    end_date = ndb.StringProperty()

# class Rental(ndb.Model):
#     id = ndb.StringProperty()
#     account = ndb.StringProperty()
#     car = ndb.StringProperty()
#     start_date = ndb.DateProperty()
#     end_date = ndb.DateProperty()


# [END Data classes]

# [START Handlers]


class AccountHandler(webapp2.RequestHandler):
    def post(self):
        #try:
            account_data = json.loads(self.request.body)
            #header_data = json.loads(self.request.headers)
            new_account = Account(name=account_data['name'],
                                  address=account_data['address'],
                                  phone_number=account_data['phone_number'],
                                  d_license=account_data['d_license'],
                                  dl_state=account_data['dl_state'],
                                  auth=self.request.headers['authorization'])
            new_account.put()
            new_account.id = new_account.key.urlsafe()
            new_account.put()
            account_dict = new_account.to_dict()
            account_dict['self'] = '/account/' + new_account.id
            self.response.write(json.dumps(account_dict))
        #except:
         #   self.response.set_status(400)
          #  self.response.write("Invalid Request")

    def get(self, id=None):
        try:
            if id:
                b = ndb.Key(urlsafe=id).get()
                if self.request.headers['authorization'] == b.auth or self.request.headers['authorization'] == admin_id :
                    b_d = b.to_dict()
                    b_d['self'] = "/account/" + id
                    self.response.write(json.dumps(b_d))
                else:
                    self.response.set_status(403)
                    self.response.write("Can only get your own account")
            else:
                if self.request.headers['authorization'] == admin_id:
                    all_accounts = Account.query().fetch()
                    serialized_accounts = filter_results(all_accounts, '/account/')
                    self.response.write(json.dumps(serialized_accounts))
                else:
                    self.response.set_status(403)
                    self.response.write("Only admins can get a list of accounts")
        except:
            self.response.set_status(404)
            self.response.write("Account Not Found")

    def patch(self, id=None):
        if id:
            # get request body
            patch_data = json.loads(self.request.body)

            # get account in question
            account = ndb.Key(urlsafe=id).get()

            # error out if updating wrong data
            if patch_data.get('id'):
                self.response.set_status(403)
                self.response.write("Cannot update ID")
            elif self.request.headers['authorization'] != account.auth:
                self.response.set_status(403)
                self.response.write("Can only update your own account")
            else:
                # Update Name
                if patch_data.get('name'):
                    account.name = patch_data['name']
                   # self.response.write("Updated account name\n")
                # Update Address
                if patch_data.get('address'):
                    account.address = patch_data['address']
                    #self.response.write("Updated account address\n")
                # Update Phone_number
                if patch_data.get('phone_number'):
                    account.phone_number = patch_data['phone_number']
                    #self.response.write("Updated account phone number\n")
                # Update D_license
                if patch_data.get('d_license'):
                    account.d_license = patch_data['d_license']
                    #self.response.write("Updated account driver's license\n")
                # Update Dl_state
                if patch_data.get('dl_state'):
                    account.dl_state = patch_data['dl_state']
                    #self.response.write("Updated account driver's license state\n")
                account.put()
                account_dict = account.to_dict()
                self.response.write(json.dumps(account_dict))
        else:
            self.response.set_status(400)
            self.response.write("Must provide id.")

    def put(self, id=None):
        if id:
        # get request body
            put_data = json.loads(self.request.body)

            # get account in question
            account = ndb.Key(urlsafe=id).get()

            # error out if updating wrong data
            if put_data.get('id'):
                self.response.set_status(403)
                self.response.write("Cannot update ID")
            elif self.request.headers['authorization'] != account.auth:
                self.response.set_status(403)
                self.response.write("Can only update your own account")
            else:
                # Update all fields
                try:
                    account.name = put_data['name']
                    account.address = put_data['address']
                    account.phone_number = put_data['phone_number']
                    account.d_license = put_data['d_license']
                    account.dl_state = put_data['dl_state']
                    account.put()
                    account_dict = account.to_dict()
                    self.response.write(json.dumps(account_dict))
                except:
                    self.response.set_status(400)
                    self.response.write("Must provide all values")
        else:
            self.response.set_status(400)
            self.response.write("Must provide id.")

    def delete(self, id=None):
            try:
                if id:

                    b = ndb.Key(urlsafe=id).get()
                    if self.request.headers['authorization'] == b.auth or self.request.headers['authorization'] == admin_id:
                        all_cars = Car.query(Car.current_account == b.id)
                        if all_cars:
                            car = all_cars.get()
                            car.current_account = None
                            car.start_date = None
                            car.end_date = None
                            car.put()

                        b.key.delete()
                        self.response.write("Deleted account")
                    else:
                        self.response.set_status(403)
                        self.response.write("Can only delete your own account")
                else:
                    self.response.set_status(400)
                    self.response.write("Must provide id.")

            except:
                self.response.set_status(400)
                self.response.write("Invalid Request")


class CarHandler(webapp2.RequestHandler):

    def post(self):


        try:
            if self.request.headers['authorization'] == admin_id:
                car_data = json.loads(self.request.body)
                new_car = Car(make=car_data['make'],
                          model=car_data['model'],
                          color=car_data['color'],
                          year=car_data['year'],
                          v_license=car_data['v_license'],
                          v_state=car_data['v_state'])
                new_car.put()
                new_car.id = new_car.key.urlsafe()
                new_car.put()
                car_dict = new_car.to_dict()
                car_dict['self'] = '/car/' + new_car.id
                self.response.write(json.dumps(car_dict))
            else:
                self.response.set_status(403)
                self.response.write("Only admins can create cars")
        except:
            self.response.set_status(400)
            self.response.write("Invalid Request")

    def get(self, id=None):
        try:
            if id:
                s = ndb.Key(urlsafe=id).get()
                s_d = s.to_dict()
                s_d['self'] = "/car/" + id
                self.response.write(json.dumps(s_d))
            else:
                all_cars = Car.query().fetch()
                serialized_cars = filter_results(all_cars, '/car/')
                self.response.write(json.dumps(serialized_cars))
        except:
            self.response.set_status(404)
            self.response.write("Car Not Found")

    def patch(self, id=None):
        if id:
            # get request body
            patch_data = json.loads(self.request.body)

            # get car in question
            car = ndb.Key(urlsafe=id).get()

            # error out if updating wrong data
            if patch_data.get('current_account') or patch_data.get('start_date') or patch_data.get('end_date'):
                self.response.set_status(403)
                self.response.write("Cannot update rental information via car")
            elif patch_data.get('id'):
                self.response.set_status(403)
                self.response.write("Cannot update ID")
            elif self.request.headers['authorization'] != admin_id:
                self.response.set_status(403)
                self.response.write("Only admins can edit cars")
            else:
                # Update make
                if patch_data.get('make'):
                    car.make = patch_data['make']
                    #self.response.write("Updated car make\n")
                # Update model
                if patch_data.get('model'):
                    car.model = patch_data['model']
                    #self.response.write("Updated car model\n")
                # Update Color
                if patch_data.get('color'):
                    car.color = patch_data['color']
                    #self.response.write("Updated car color\n")
                # Update Year
                if patch_data.get('year'):
                    car.year = patch_data['year']
                    #self.response.write("Updated car phone number\n")
                # Update V_license
                if patch_data.get('v_license'):
                    car.v_license = patch_data['v_license']
                    #self.response.write("Updated car license\n")
                # Update V_state
                if patch_data.get('v_state'):
                    car.v_state = patch_data['v_state']
                    #self.response.write("Updated car's license state\n")
                car.put()
                car_dict = car.to_dict()
                self.response.write(json.dumps(car_dict))
        else:
            self.response.set_status(400)
            self.response.write("Must provide id.")

    def delete(self, id=None):
            try:
                if id:
                    if self.request.headers['authorization'] == admin_id:
                        car = ndb.Key(urlsafe=id).get()
                        if car.current_account is not None:
                            account = ndb.Key(urlsafe=car.current_account).get()
                            account.at_sea = True
                            account.put()

                        car.key.delete()
                        self.response.write("Deleted car")
                    else:
                        self.response.set_status(403)
                        self.response.write("Only admins can edit cars")
                else:
                    self.response.set_status(400)
                    self.response.write("Must provide id.")

            except:
                self.response.set_status(400)
                self.response.write("Invalid Request")


class RentalHandler(webapp2.RequestHandler):
    def put(self, id=None):
        try:
            if id:
                rental_data = json.loads(self.request.body)
                account_id = rental_data['account_id']
                car = ndb.Key(urlsafe=id).get()
                if car.current_account is None:
                    car.current_account = account_id
                    car.start_date = rental_data['start_date']
                    car.end_date = rental_data['end_date']
                    car.put()
                    car_dict = car.to_dict()
                    self.response.write(json.dumps(car_dict))
                else:
                    self.response.set_status(403)
                    self.response.write("Car already rented")
            else:
                self.response.set_status(400)
                self.response.write("Invalid url, need car id")
        except:
            self.response.set_status(400)
            self.response.write("Invalid Request")

    def get(self, id=None):
        #try:
            if id:
                b = ndb.Key(urlsafe=id).get()
                if self.request.headers['authorization'] == b.auth or self.request.headers['authorization'] == admin_id:
                    all_cars = Car.query(Car.current_account == b.id).fetch()
                    serialized_cars = filter_results(all_cars, '/car/')
                    self.response.write(json.dumps(serialized_cars))
                else:
                    self.response.set_status(403)
                    self.response.write("Can only get your own account")
            else:
                if self.request.headers['authorization'] == admin_id:
                    all_cars = Car.query(Car.current_account != None).fetch()
                    serialized_cars = filter_results(all_cars, '/car/')
                    self.response.write(json.dumps(serialized_cars))
                else:
                    self.response.set_status(403)
                    self.response.write("Only admins can get a list of all rentals")
        #except:
         #   self.response.set_status(404)
          #  self.response.write("Account Not Found")


    def patch(self, id=None):
        try:
            if id:
                patch_data = json.loads(self.request.body)
                car = ndb.Key(urlsafe=id).get()
                if car.current_account is None:
                    self.response.set_status(400)
                    self.response.write("Invalid Request, can only modify rental data")
                else:
                    if patch_data.get('account_id'):
                        car.current_account = patch_data['account_id']
                        #self.response.write("Rental account updated \n")
                    if patch_data.get('start_date'):
                        car.start_date = patch_data['start_date']
                        #self.response.write("Rental start date updated")
                    if patch_data.get('end_date'):
                        car.end_date = patch_data['end_date']
                        #self.response.write("Rental end date updated")
                    car.put()
                    car_dict = car.to_dict()
                    self.response.write(json.dumps(car_dict))
            else:
                self.response.set_status(400)
                self.response.write("Invalid url, need car id")
        except:
            self.response.set_status(400)
            self.response.write("Invalid Request")




# [END Handlers]


# [START main_page]
class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write("Welcome to Dock Management")
# [END main_page]

allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/account', AccountHandler),
    ('/account/(.*)', AccountHandler),
    ('/car', CarHandler),
    ('/car/(.*)/rental', RentalHandler),
    ('/car/(.*)', CarHandler),
    ('/rental/(.*)', RentalHandler),

], debug=True)
# [END app]
