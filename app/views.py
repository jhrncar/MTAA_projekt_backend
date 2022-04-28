from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from django.http import HttpResponse
import psycopg2
import math
import json
from django.db import connection, IntegrityError
from datetime import datetime, date
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from django.db.models import Q
from django.contrib.auth.models import auth

from .models import User, Items_categories, Districts, Statuses, Advertisments
from django.db import models


@csrf_exempt
def check_email(request):
    if request.method == 'GET':

        error = 0

        email = (request.GET.get('email', default=""))

        email_unique = User.objects.all().filter(Q(email=email)).count()
        print(email_unique)
        if email_unique != 0:
            error += 1

        if error != 0:

            response = HttpResponse()
            response.status_code = 403
        else:

            response = HttpResponse()

            response.status_code = 200

        return response


@csrf_exempt
def check_username(request):

    if request.method == 'GET':

        error = 0

        username = (request.GET.get('username', default=""))

        user_name_unique = User.objects.all().filter(Q(username=username)).count()

        if user_name_unique != 0:
            error += 1

        if error != 0:

            response = HttpResponse()
            response.status_code = 403
        else:

            response = HttpResponse()

            response.status_code = 200

        return response


@csrf_exempt
def register(request):
    # POST request

    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)

        len_list = len(data)

        # nazvy parametrov ktore musia byt v body
        required_parameters = ["user_name",
                               "first_name", "last_name", "email", "password"]
        optional_parameters = ["city", "street",
                               "zipcode", "phone", "district"]

        # pole v ktorom budu ulozene hodnoty parametrov
        parameters_values = []

        errors = []

        error = 0

        for i in range(5):
            # ziskanie hodnot textovych parametrov
            if required_parameters[i] in data:
                if data[required_parameters[i]] == None:
                    error += 1
                    errors.append(
                        {"field": required_parameters[i], "reasons": ["requred"]})

                if i == 3:
                    mail = data[required_parameters[i]]
                    j = len(mail)
                    dot = 0
                    at = 0
                    at_position = 0
                    dot_position = 0
                    for k in range(j):
                        if mail[k] == '@' and at == 0:
                            at = 1
                            at_position = k
                            continue
                        if mail[k] == '.' and dot == 0 and at != 0:
                            dot = 1
                            dot_position = k
                            continue
                        if mail[k] == '@' and at != 0:
                            print("1")
                            error += 1
                            errors.append(
                                {"field": required_parameters[i], "reasons": ["invalid mail"]})
                        if mail[k] == '.' and dot != 0:
                            print("2")
                            error += 1
                            errors.append(
                                {"field": required_parameters[i], "reasons": ["invalid mail"]})
                    if at_position > dot_position:
                        print("3")
                        error += 1
                        errors.append(
                            {"field": required_parameters[i], "reasons": ["invalid mail"]})

                parameters_values.append(data[required_parameters[i]])

            else:
                error += 1
                errors.append(
                    {"field": required_parameters[i], "reasons": ["required"]})

            city = None
            street = None
            zip_code = None
            phone = None
            district_id = None

            for i in range(5):
                # ziskanie hodnot textovych parametrov
                if optional_parameters[i] in data:
                    if i == 0:
                        city = data[optional_parameters[i]]
                    if i == 1:
                        street = data[optional_parameters[i]]
                    if i == 2:
                        zip_code = data[optional_parameters[i]]
                    if i == 3:
                        phone_data = data[optional_parameters[i]]
                        if phone_data != None:
                            j = len(phone_data)
                            if phone_data[0] != '+':
                                if phone_data[0] < '0' or phone_data[0] > '9':
                                    error += 1
                                    errors.append(
                                        {"field": optional_parameters[i], "reasons": ["invalid phone number"]})
                            for k in range(1, j):
                                if phone_data[k] < '0' or phone_data[k] > '9':
                                    error += 1
                                    errors.append(
                                        {"field": optional_parameters[i], "reasons": ["invalid phone number"]})
                            phone = data[optional_parameters[i]]
                    if i == 4:
                        district_id = None
                        district_name = data[optional_parameters[i]]
                        district_exists = Districts.objects.all().filter(Q(name=district_name)).count()

                        if district_exists == 0:
                            error += 1
                            errors.append({"field": "district", "reasons": [
                                          "district doesnt exists"]})
                        else:

                            district_id = Districts.objects.values_list(
                                'id').filter(Q(name=district_name))

        email_unique = User.objects.all().filter(Q(email=mail)).count()

        if email_unique != 0:
            error += 1
            errors.append({"field": "email", "reasons": ["not_unique"]})

        user_name_unique = User.objects.all().filter(
            Q(username=data["user_name"])).count()

        if user_name_unique != 0:
            error += 1
            errors.append({"field": "user_name", "reasons": ["not_unique"]})

            # ak je nejaky parameter vadny alebo nie je zadany vrati sa error
        if error != 0:
            result = {
                "errors": errors
            }
            response = JsonResponse(result)
            response.status_code = 422
        else:

            # pridanie zaznamu do databazy

            user_registration = User.objects.create_user(username=parameters_values[0], first_name=parameters_values[1],
                                                         last_name=parameters_values[2], email=parameters_values[3],
                                                         password=parameters_values[4], city=city,
                                                         street=street, zip_code=zip_code,
                                                         phone=phone, district_id=district_id)

            user_registration.save()

            response = HttpResponse()

            response.status_code = 201
        return response


@csrf_exempt
def login(request):
    # POST request

    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)

        errors = []

        error = 0

        if "user_name" in data:
            username = data["user_name"]
        else:
            error += 1
            errors.append({"field": "user_name", "reasons": ["required"]})

        if "password" in data:
            password = data["password"]
        else:
            error += 1
            errors.append({"field": "password", "reasons": ["required"]})

        if error != 0:
            result = {
                "errors": errors
            }
            response = JsonResponse(result)
            response.status_code = 401

            return response
        else:

            if request.user.is_authenticated:
                errors.append({"login failed": "user already logged in"})

                result = {
                    "errors": errors
                }

                response = JsonResponse(result)
                response.status_code = 403

                return response

            else:

                user = auth.authenticate(username=username, password=password)

                if user is not None:
                    auth.login(request, user)

                    response = HttpResponse()
                    response.status_code = 200

                    return response

                else:

                    errors.append({"login failed": "invalid credentials"})

                    result = {
                        "errors": errors
                    }

                    response = JsonResponse(result)
                    response.status_code = 401

                    return response


@csrf_exempt
def logout(request):
    # POST request

    if request.method == 'POST':
        if request.user.is_authenticated:
            auth.logout(request)

            response = HttpResponse()
            response.status_code = 200

            return response

        else:
            errors = []

            errors.append({"logout_failed": "no_user_is_logged_in"})

            result = {
                "errors": errors
            }

            response = JsonResponse(result)
            response.status_code = 401

            return response


@csrf_exempt
def get_categories(request):

    if request.method == 'GET':

        categories = Items_categories.objects.all().values("id", "name", "picture")

        response = HttpResponse(json.dumps(
            list(categories)), content_type="application/json")

        response.status_code = 200

        return response


@csrf_exempt
def get_districts(request):

    if request.method == 'GET':

        districts = Districts.objects.all().values("id", "name")

        response = HttpResponse(json.dumps(
            list(districts)), content_type="application/json")

        response.status_code = 200

        return response


@csrf_exempt
def my_profile(request):

    if request.method == 'GET':
        if request.user.is_authenticated:

            user_profile = User.objects.select_related(
                'district').get(id=request.user.id)
            try:
                district = user_profile.district.name
            except:
                district = None

            items = {"user_name": user_profile.username,
                     "first_name": user_profile.first_name,
                     "last_name": user_profile.last_name,
                     "email": user_profile.email,
                     "district": district,
                     "city": user_profile.city,
                     "zip_code": user_profile.zip_code,
                     "street": user_profile.street,
                     "phone": user_profile.phone
                     }

            result = {
                "items": items
            }

            response = JsonResponse(result)
            response.status_code = 200

            return response

        else:
            errors = []

            errors.append({"unable to load profile": "no user is logged in"})

            result = {
                "errors": errors
            }

            response = JsonResponse(result)
            response.status_code = 401

            return response


@csrf_exempt
def user_profile(request, username):

    if request.method == 'GET':
        if request.user.is_authenticated:

            errors = []
            count = User.objects.filter(username=username).count()

            count = int(count)

            if count == 0:
                errors.append(
                    {"unable to load user profile": "user not found"})

                result = {
                    "errors": errors
                }

                response = JsonResponse(result)
                response.status_code = 404
                return response

            user_profile = User.objects.select_related(
                'district').get(username=username)

            if user_profile.district == None:

                items = {"user_name": user_profile.username,
                         "first_name": user_profile.first_name,
                         "last_name": user_profile.last_name,
                         "email": user_profile.email,
                         "district": None,
                         "city": user_profile.city,
                         "zip_code": user_profile.zip_code,
                         "street": user_profile.street,
                         "phone": user_profile.phone
                         }
            else:

                items = {"user_name": user_profile.username,
                         "first_name": user_profile.first_name,
                         "last_name": user_profile.last_name,
                         "email": user_profile.email,
                         "district": user_profile.district.name,
                         "city": user_profile.city,
                         "zip_code": user_profile.zip_code,
                         "street": user_profile.street,
                         "phone": user_profile.phone
                         }

            result = {
                "items": items
            }

            response = JsonResponse(result)
            response.status_code = 200

            return response

        else:
            errors = []

            errors.append({"unable to load user profile": "login requested"})

            result = {
                "errors": errors
            }

            response = JsonResponse(result)
            response.status_code = 403

            return response


@csrf_exempt
def ads(request):
    if request.method == 'GET':
        page = (request.GET.get('page', default=1))
        name = (request.GET.get('name', default=""))
        category = (request.GET.get('category', default=""))
        district = (request.GET.get('district', default=""))
        min_prize = (request.GET.get('min_prize', default=-1))
        max_prize = (request.GET.get('max_prize', default=-1))

        error = 0
        errors = []

        try:
            page = int(page)
        except:
            error = error + 1
            errors.append({"page": "not number"})

        try:
            min_prize = int(min_prize)
        except:
            error = error + 1
            errors.append({"min_prize": "not number"})

        try:
            max_prize = int(max_prize)
        except:
            error = error + 1
            errors.append({"max_prize": "not number"})

        category = str(category)

        page_number = page
        page = (page - 1) * 10

        query = Q()

        if name != "":
            query = Q(name__icontains=name)

        if category != "":

            valid = 1
            category_name = ""

            try:
                category_name = Items_categories.objects.get(name=category)
            except:
                error = error + 1
                errors.append({"category": "invalid value"})
                valid = 0

            if valid == 1:
                query &= Q(category_id=category_name.id)

        if district != "":

            valid = 1
            district_name = ""

            try:
                district_name = Districts.objects.get(name=district)
            except:
                error = error + 1
                errors.append({"district": "invalid value"})
                valid = 0

            if valid == 1:
                query &= Q(district_id=district_name.id)

        if min_prize != -1:
            query &= Q(prize__gte=min_prize)

        if max_prize != -1:
            query &= Q(prize__lte=max_prize)

        if error != 0:
            result = {
                "errors": errors
            }

            response = JsonResponse(result)
            response.status_code = 422

            return response

        result = Advertisments.objects.filter(
            query).order_by('-created_at')[page:page + 10]
        count = Advertisments.objects.filter(query).count()

        items = list(result.values('id', 'name', 'description', 'prize',
                                   'picture', 'city', 'street', 'zip_code', 'category__name',
                                   'district__name', 'status__name', 'owner__username'))

        for records in items:
            records['category'] = records.pop('category__name')
            records['district'] = records.pop('district__name')
            records['status'] = records.pop('status__name')
            records['owner'] = records.pop('owner__username')

        count = float(count)

        max_page = count / 10
        max_page = int(math.ceil(max_page))
        count = int(count)
        result = {
            "items": items,
            "metadata": {
                "page": page_number,
                "per_page": 10,
                "pages_total": max_page,
                "records_total": count
            }
        }

        response = JsonResponse(result)
        response.status_code = 200

        return response


@csrf_exempt
def latest_ads(request):
    if request.method == 'GET':

        result = Advertisments.objects.filter().order_by('-created_at')[0:10]

        items = list(result.values('id', 'name', 'description', 'prize',
                                   'picture', 'city', 'street', 'zip_code', 'category__name',
                                   'district__name', 'status__name', 'owner__username'))

        for records in items:
            records['category'] = records.pop('category__name')
            records['district'] = records.pop('district__name')
            records['status'] = records.pop('status__name')
            records['owner'] = records.pop('owner__username')

        result = {
            "items": items

        }

        response = JsonResponse(result)
        response.status_code = 200

        return response


@csrf_exempt
def favourite_ads(request):
    if request.method == 'GET':

        if request.user.is_authenticated:
            page = (request.GET.get('page', default=1))
            name = (request.GET.get('name', default=""))
            category = (request.GET.get('category', default=""))
            district = (request.GET.get('district', default=""))
            min_prize = (request.GET.get('min_prize', default=-1))
            max_prize = (request.GET.get('max_prize', default=-1))

            error = 0
            errors = []

            try:
                page = int(page)
            except:
                error = error + 1
                errors.append({"page": "not number"})

            try:
                min_prize = int(min_prize)
            except:
                error = error + 1
                errors.append({"min_prize": "not number"})

            try:
                max_prize = int(max_prize)
            except:
                error = error + 1
                errors.append({"max_prize": "not number"})

            category = str(category)

            page_number = page
            page = (page - 1) * 10

            query = Q()

            if name != "":
                query = Q(name__icontains=name)

            if category != "":

                valid = 1
                category_name = ""

                try:
                    category_name = Items_categories.objects.get(name=category)
                except:
                    error = error + 1
                    errors.append({"category": "invalid value"})
                    valid = 0

                if valid == 1:
                    query &= Q(category_id=category_name.id)

            if district != "":

                valid = 1
                district_name = ""

                try:
                    district_name = Districts.objects.get(name=district)
                except:
                    error = error + 1
                    errors.append({"district": "invalid value"})
                    valid = 0

                if valid == 1:
                    query &= Q(district_id=district_name.id)

            if min_prize != -1:
                query &= Q(prize__gte=min_prize)

            if max_prize != -1:
                query &= Q(prize__lte=max_prize)

            if error != 0:
                result = {
                    "errors": errors
                }

                response = JsonResponse(result)
                response.status_code = 422

                return response

            logged_user = User.objects.get(id=request.user.id)

            favourite = logged_user.favourite_ads.filter(query)
            count = logged_user.favourite_ads.filter(query).count()

            items = list(favourite.values('id', 'name', 'description', 'prize',
                                          'picture', 'city', 'street', 'zip_code', 'category__name',
                                          'district__name', 'status__name', 'owner__username'
                                          ))
            print(type(items))

            #items = list(result.values('favourite_ads__id'))

            for records in items:
                records['category'] = records.pop('category__name')
                records['district'] = records.pop('district__name')
                records['status'] = records.pop('status__name')
                records['owner'] = records.pop('owner__username')

            count = float(count)

            max_page = count / 10
            max_page = int(math.ceil(max_page))
            count = int(count)
            result = {
                "items": items,

            }

            response = JsonResponse(result)
            response.status_code = 200

            return response

        else:
            errors = []

            errors.append(
                {"unable to load favourite ads": "no user is logged in"})

            result = {
                "errors": errors
            }

            response = JsonResponse(result)
            response.status_code = 401

            return response


@csrf_exempt
def my_ads(request):

    if request.method == 'GET':
        if request.user.is_authenticated:

            page = (request.GET.get('page', default=1))

            try:
                page = int(page)
            except:

                errors.append({"page": "not number"})

                result = {
                    "errors": errors
                }

                response = JsonResponse(result)
                response.status_code = 422

                return response

            page_number = page
            page = (page-1) * 10

            data = Advertisments.objects.filter(
                owner_id=request.user.id).order_by('-created_at')
            count = Advertisments.objects.filter(
                owner_id=request.user.id).count()

            items = list(data.values('id', 'name', 'description', 'prize',
                                     'picture', 'city', 'street', 'zip_code', 'category__name',
                                     'district__name', 'status__name', 'owner__username'))

            for records in items:
                records['category'] = records.pop('category__name')
                records['district'] = records.pop('district__name')
                records['status'] = records.pop('status__name')
                records['owner'] = records.pop('owner__username')

            count = float(count)

            max_page = count / 10
            max_page = int(math.ceil(max_page))
            count = int(count)
            result = {
                "items": items,
            }

            response = JsonResponse(result)
            response.status_code = 200

            return response

        else:
            errors = []

            errors.append({"unable to load users ads": "no user is logged in"})

            result = {
                "errors": errors
            }

            response = JsonResponse(result)
            response.status_code = 401

            return response


@csrf_exempt
def ad_detail(request, id):

    if request.method == 'GET':

        id = str(id)
        errors = []

        count = Advertisments.objects.filter(id=id).count()

        count = int(count)

        if count == 0:
            errors.append({"unable to load ad detail": "ad not found"})

            result = {
                "errors": errors
            }

            response = JsonResponse(result)
            response.status_code = 404
            return response

        data = Advertisments.objects.filter(id=id)

        items = list(data.values('id', 'name', 'description', 'prize',
                                 'picture', 'city', 'street', 'zip_code', 'category__name',
                                 'district__name', 'status__name', 'owner__username'))

        for records in items:
            records['category'] = records.pop('category__name')
            records['district'] = records.pop('district__name')
            records['status'] = records.pop('status__name')
            records['owner'] = records.pop('owner__username')

        result = {
            "items": items
        }

        response = JsonResponse(result)
        response.status_code = 200

        return response


@csrf_exempt
def get_image(request, name):
    if request.method == 'GET':
        location = 'media/'+name
        try:
            img = open(location, 'rb')

            response = FileResponse(img)
            response.status_code = 200
            return response
        except IOError:
            response = HttpResponse()
            response.status_code = 404
            return response


@csrf_exempt
def create_new_ad(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                data = json.loads(request.POST["json"])
            except BaseException:
                response = JsonResponse({"errors": "errors_in_request_body"})
                response.status_code = 422
                return response
            required_fields = ["name", "price", "district",
                               "city", "category", "description"]
            optional_fields = ["street", "zip_code"]
            errors = []
            for req in required_fields:
                if req not in data:
                    errors.append({req: "required"})
            else:
                if len(errors) != 0:
                    response = JsonResponse({"errors": errors})
                    response.status_code = 422
                    return response

            try:
                category = Items_categories.objects.get(name=data["category"])
            except models.ObjectDoesNotExist:
                response = JsonResponse(
                    {"errors": {"create_failed": "category_value_doesnt_exist"}})
                print(data["category"])
                response.status_code = 422
                return response
            try:
                district = Districts.objects.get(name=data["district"])
            except models.ObjectDoesNotExist:
                response = JsonResponse(
                    {"errors": {"create_failed": "district_value_doesnt_exist"}})

                response.status_code = 422
                return response

            for field in optional_fields:
                if field not in data:
                    data[field] = None

            if "file" in request.FILES:
                file = request.FILES["file"]
            else:
                file = None
            status = Statuses.objects.get(id=1)
            price = data["price"]

            try:
                int(price)
            except models.ObjectDoesNotExist:
                response = JsonResponse({"errors": {"price": "not number"}})
                print(type(price))
                response.status_code = 422

                return response

            new = Advertisments(
                name=data["name"],
                description=data["description"],
                prize=data["price"],
                picture=file,
                city=data["city"],
                street=data["street"],
                zip_code=data["zip_code"],
                category=category,
                status=status,
                district=district,
                owner_id=request.user.id
            )
            new.save()
            response = HttpResponse()
            response.status_code = 201
            return response

        else:
            response = JsonResponse(
                {"errors": {"create_failed": "no_user_is_logged_in"}})
            response.status_code = 401
            return response


@csrf_exempt
def add_favourite_ads(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                data = json.loads(request.body.decode("utf-8"))
            except BaseException:
                response = JsonResponse({"errors": "errors_in_request_body"})
                response.status_code = 422
                return response

            required_fields = ["ad_id"]
            errors = []

            for req in required_fields:
                if req not in data:
                    errors.append({req: "required"})

            if len(errors) != 0:
                response = JsonResponse({"errors": errors})
                response.status_code = 422
                return response
            try:
                ad = Advertisments.objects.get(id=data["ad_id"])
                if ad.owner.id == request.user.id:
                    response = JsonResponse(
                        {"errors": {"add_failed": "unable_to_add_own_ad"}})
                    response.status_code = 403
                    return response

            except models.ObjectDoesNotExist:
                response = JsonResponse(
                    {"errors": {"add_failed": "ad_doesnt_exist"}})
                response.status_code = 404
                return response

            user_profile = User.objects.get(id=request.user.id)

            user_profile.favourite_ads.add(ad)
            user_profile.favourite_ads.save()  # skontrolovat
            response = HttpResponse()
            response.status_code = 200
            return response

        else:
            response = JsonResponse(
                {"errors": {"create_failed": "no_user_is_logged_in"}})
            response.status_code = 401
            return response


@csrf_exempt
def update_profile(request):
    if request.method == 'PUT':
        if request.user.is_authenticated:
            try:
                data = json.loads(request.body.decode("utf-8"))
                print(data)
            except BaseException:
                print("xx")
                response = JsonResponse(
                    {"errors": "unable_to_load_request_body"})
                response.status_code = 422
                return response
            required_fields = ["username", "first_name", "last_name"]
            optional_fields = ["city", "street",
                               "zip_code", "phone", "district"]
            errors = []
            for req in required_fields:
                if req not in data:
                    errors.append({req: "required"})
            else:
                if len(errors) != 0:
                    print("aa")
                    response = JsonResponse({"errors": errors})
                    response.status_code = 422
                    return response
            current_user = User.objects.get(id=request.user.id)
            if current_user.deleted_at != None:
                print("affa")
                response = JsonResponse(
                    {"errors": {"update_failed": "user_doesnt_exist"}})
                response.status_code = 422
                return response
            if data["city"] == None:
                data["city"] = current_user.city
            if data["street"] == None:
                data["street"] = current_user.street
            if data["zip_code"] == None:
                data["zip_code"] = current_user.zip_code
            if data["phone"] == None:
                data["phone"] = current_user.phone
            if data["district"] == None:
                try:
                    district = Districts.objects.get(name=current_user.district.name)
                except:
                    district = None
            else:
                try:
                    district = Districts.objects.get(name=data["district"])
                except models.ObjectDoesNotExist:
                    print("aadsdsdsds")
                    response = JsonResponse(
                        {"errors": {"update_failed": "district_value_doesnt_exist"}})
                    response.status_code = 422
                    return response
                """
                            update hesla, emailu bude ked tak samostatny endpoint
                            """
            try:
                User.objects.filter(id=request.user.id).update(
                    last_name=data["last_name"],
                    first_name=data["first_name"],
                    username=data["username"],
                    district=district,
                    city=data["city"],
                    street=data["street"],
                    zip_code=data["zip_code"],
                    phone=data["phone"]
                )

                response = HttpResponse()
                response.status_code = 201
                return response
            except IntegrityError:
                response = JsonResponse(
                    {"errors": {"update_failed": "invalid_value"}})
                response.status_code = 422
                return response

        else:
            response = JsonResponse(
                {"errors": {"create_failed": "no_user_is_logged_in"}})
            response.status_code = 401
            return response


@csrf_exempt
def update_ad(request):
    if request.method == 'POST':  # TODO musi byt POST, inac nejde request
        if request.user.is_authenticated:
            try:
                data = json.loads(request.POST["json"])
                print(data)
            except BaseException:
                response = JsonResponse(
                    {"errors": "unable_to_load_request_body"})
                response.status_code = 422
                return response
            required_fields = ["ad_id", "name", "description",
                               "price", "city", "category", "district"]
            optional_fields = ["street", "zip_code"]
            errors = []
            for req in required_fields:
                if req not in data:
                    errors.append({req: "required"})
            else:
                if len(errors) != 0:
                    response = JsonResponse({"errors": errors})
                    response.status_code = 422
                    return response
                try:
                    ad = Advertisments.objects.get(id=data["ad_id"])
                    district = Districts.objects.get(name=data["district"])
                    status = Statuses.objects.get(name="Dostupný")
                    category = Items_categories.objects.get(
                        name=data["category"])
                    if ad.deleted_at != None:
                        raise models.ObjectDoesNotExist
                except models.ObjectDoesNotExist:
                    response = JsonResponse(
                        {"errors": {"update_failed": "value_doesnt_exist"}})
                    response.status_code = 422
                    return response
                if request.user.id != ad.owner_id:
                    response = JsonResponse(
                        {"errors": {"update_failed": "ad_belongs_to_different_user"}})
                    response.status_code = 403
                    return response
                if "file" in request.FILES:
                    file = request.FILES["file"]
                    ad.picture = file
                    ad.save()
                else:
                    file = None
                if data["street"] == '':
                    data["street"] = None
                if data["zip_code"] == '':
                    data["zip_code"] = None
                try:
                    if not type(data["price"]) is int:
                        response = JsonResponse(
                            {"errors": {"price": "not number"}})
                        response.status_code = 422
                        return response
                    Advertisments.objects.filter(id=data['ad_id'], owner_id=request.user.id).update(
                        name=data["name"],
                        description=data["description"],
                        prize=data["price"],
                        city=data["city"],
                        street=data["street"],
                        zip_code=data["zip_code"],
                        category=category,
                        status=status,
                        district=district
                    )
                except IntegrityError:
                    response = JsonResponse(
                        {"errors": {"update_failed": "invalid_value"}})
                    response.status_code = 422
                    return response
                response = HttpResponse()
                response.status_code = 204
                return response
        else:
            response = JsonResponse(
                {"errors": {"create_failed": "no_user_is_logged_in"}})
            response.status_code = 401
            return response


@csrf_exempt
def delete_ad(request):
    if request.method == 'DELETE':
        if request.user.is_authenticated:
            try:
                data = json.loads(request.body.decode("utf-8"))
            except BaseException:
                response = JsonResponse(
                    {"errors": "unable_to_load_request_body"})
                response.status_code = 422
                return response
            required_fields = ["ad_id"]
            errors = []
            for req in required_fields:
                if req not in data:
                    errors.append({req: "required"})
            else:
                if len(errors) != 0:
                    response = JsonResponse({"errors": errors})
                    response.status_code = 422
                    return response
            try:
                ad = Advertisments.objects.get(id=data["ad_id"])
            except models.ObjectDoesNotExist:
                response = JsonResponse(
                    {"errors": {"delete_failed": "ad_doesnt_exist"}})
                response.status_code = 404
                return response
            if ad.owner.id == request.user.id:
                Advertisments.objects.filter(id=data["ad_id"]).delete()
                response = HttpResponse()
                response.status_code = 200
                return response
            else:
                response = JsonResponse(
                    {"errors": "ad_belongs_to_different_user"})
                response.status_code = 403
                return response
        else:
            response = JsonResponse(
                {"errors": {"create_failed": "no_user_is_logged_in"}})
            response.status_code = 401
            return response


@csrf_exempt
def delete_favourite(request):
    if request.method == 'DELETE':
        if request.user.is_authenticated:
            try:
                data = json.loads(request.body.decode("utf-8"))
            except BaseException:
                response = JsonResponse(
                    {"errors": "unable_to_load_request_body"})
                response.status_code = 422
                return response
            required_fields = ["ad_id"]
            errors = []
            for req in required_fields:
                if req not in data:
                    errors.append({req: "required"})
            else:
                if len(errors) != 0:
                    response = JsonResponse({"errors": errors})
                    response.status_code = 422
                    return response

            user = User.objects.get(id=request.user.id)

            ad_to_remove = user.favourite_ads.filter(id=data["ad_id"])

            id_to_remove = list(ad_to_remove.values('id'))

            if not id_to_remove:
                response = JsonResponse(
                    {"errors": {"delete_failed": "ad_is_not_in_favourites"}})
                response.status_code = 404
                return response

            user.favourite_ads.remove(id_to_remove[0]['id'])

            response = HttpResponse()
            response.status_code = 200
            return response

        else:
            response = JsonResponse(
                {"errors": {"create_failed": "no_user_is_logged_in"}})
            response.status_code = 401
            return response
