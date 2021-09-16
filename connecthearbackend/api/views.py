from django.shortcuts import render
from requests import Request, Session
from rest_framework import permissions
from rest_framework.views import APIView
from connecthearbackend.settings import DATABASES, MEDIA_ROOT
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from connecthearbackend.api.serializers import UserLoginSerializer, UserRegistrationSerializer, AdminLoginSerializer
from connecthearbackend.api.models import User, PointHistory
from django.db.models import Q
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import FileSystemStorage
from django.shortcuts import get_object_or_404, render
# Create your views here.

class UserRegistrationView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)
    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data = data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        status_code = status.HTTP_201_CREATED
        response = {
            'success': 'True',
            'status code': status_code,
            'type': 'User registered  successfully',
        }
        return Response(response, status=status_code)

class UserLoginView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer
    def post(self, request):
        serializer = self.serializer_class(data= request.data)
        serializer.is_valid(raise_exception=True)
        response = {
            'status code' : status.HTTP_200_OK,
            'token' : serializer.data['token'],
            'refresh':serializer.data['refresh'],
            'email':serializer.data['email']
        }
        status_code = status.HTTP_200_OK
        return Response(response, status=status_code)

class AdminLoginView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = AdminLoginSerializer
    def post(self, request):
        serializer = self.serializer_class(data= request.data)
        serializer.is_valid(raise_exception=True)
        response = {
            'status code' : status.HTTP_200_OK,
            'token' : serializer.data['token'],
            'refresh':serializer.data['refresh'],
            'email':serializer.data['email']
        }
        status_code = status.HTTP_200_OK
        return Response(response, status=status_code)

class UploadView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser) 
    def post(self, request):
            user = request.user
            if not user.is_superuser:
                status_code = status.HTTP_401_UNAUTHORIZED
                response = {
                    'status code' :status.HTTP_401_UNAUTHORIZED
                }
                return Response(response,status=status_code)
        # try:
            csv_file = request.FILES["csvFile"]
            if not csv_file.name.endswith('.csv'):
                response = {
                    'status code' : status.HTTP_400_BAD_REQUEST,
                }
                status_code = status.HTTP_400_BAD_REQUEST
                return Response(response, status=status_code)
            #if file is too large, return
            if csv_file.multiple_chunks():
                response = {
                    'status code' : status.HTTP_400_BAD_REQUEST,
                }
                status_code = status.HTTP_400_BAD_REQUEST
                return Response(response, status=status_code)

            file_data = csv_file.read().decode("utf-8")

            lines = file_data.split("\n")
            #loop over the lines and save them in db. If error , store as string and then display
            column = []
            uploadcsvdata = []
            for i, line in enumerate(lines):
                if i==0:
                    fields = line.strip().split(',')
                    for field in fields:
                        column.append(field)
                else:
                    fields = line.strip().split(',')
                    data_dict = {}
                    for j, filed in enumerate(fields):
                        data_dict[column[j]] = filed
                    uploadcsvdata.append(data_dict)
            if not 'id' in column:
                response = {
                    'status code' : status.HTTP_400_BAD_REQUEST,
                }
                status_code = status.HTTP_400_BAD_REQUEST
                return Response(response, status=status_code)
            for csvrow in uploadcsvdata:
                lastdate =csvrow[column[13]]
                PointHistory.objects.create(
                    memberID = csvrow[column[0]],
                    userID = csvrow[column[1]],
                    academy = csvrow[column[2]],
                    student = csvrow[column[3]],
                    country = csvrow[column[4]],
                    walletaddress = csvrow[column[6]],
                    point = csvrow[column[7]],
                    daypoint = csvrow[column[8]],
                    weekpoint = csvrow[column[9]],
                    monthpoint = csvrow[column[10]],
                    register = csvrow[column[11]],
                    package = csvrow[column[12]],
                    lastdate = csvrow[column[13]],
                )
                memberID = csvrow['id']
                user = User.objects.filter(memberID=memberID).first()
                if user:
                    user.point =csvrow[column[7]]
                    user.daypoint = csvrow[column[8]]
                    user.weekpoint =  csvrow[column[9]]
                    user.monthpoint = csvrow[column[10]]
                    user.lastdate = lastdate,
                    user.student_id = csvrow[column[3]],
                    user.country = csvrow[column[4]],
                    user.save()
            response = {
                'status code' : status.HTTP_200_OK,
            }
            status_code = status.HTTP_200_OK
            return Response(response, status=status_code)
        # except Exception as e:
        #     response = {
        #         'status code' : status.HTTP_400_BAD_REQUEST,
        #     }
        #     status_code = status.HTTP_400_BAD_REQUEST
        #     return Response(response, status=status_code)

class Account(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        user = request.user
        status_code = status.HTTP_200_OK
        data = {
            'name':user.name,
            'email':user.email,
            'memberID': user.memberID,
            'academy':user.academy,
            'user_id':user.user_id,
            'walletaddress':user.walletaddress,
            'point':user.point,
            'daypoint':user.daypoint,
            'weekpoint':user.weekpoint,
            'monthpoint':user.monthpoint,
            'student_id':user.student_id,
            'country':user.country,
            'lastdate':user.lastdate,
            'avatar':user.avatar
        }
        response = {
            'success':'True',
            'status code': status_code,
            'user' : data
        }
        return Response(response, status=status_code)


class AccountUpdate(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        data = request.data
        user.name=data['name']
        user.email=data['email']
        user.academy=data['academy']
        user.student_id=data['student_id']
        user.country=data['country']
        user.walletaddress=data['walletaddress']
        user.save()
        status_code = status.HTTP_204_NO_CONTENT
        response = {
            'success':'True',
            'status code': status_code,
            'type':'Profile Update'
        }
        return Response(response, status=status_code)

class AvatarUpdate(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        user = request.user
        avatarimgFile =  request.FILES.get('avatar', '')
        fs = FileSystemStorage()
        if(avatarimgFile):
            filename = fs.save(avatarimgFile.name, avatarimgFile)
            user.avatar = filename
            user.save()
        status_code = status.HTTP_204_NO_CONTENT
        response = {
            'success':'True',
            'status code': status_code,
            'type':'Profile Update'
        }
        return Response(response, status=status_code)

class UserList(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        user = request.user
        if not user.is_superuser:
            status_code = status.HTTP_401_UNAUTHORIZED
            response = {
                'status code' :status.HTTP_401_UNAUTHORIZED
            }
            return Response(response,status=status_code)
        data = request.data
        keywords = data['Keywords']
        pageNumber = int(data['PageNumber'])
        pageSize = int(data['PageSize'])
        offset = pageSize * (pageNumber - 1)
        if keywords!="":
            userList = User.objects.filter((~Q(is_superuser=True)) & (Q(email__contains=keywords) | Q(name__contains=keywords)))[offset:offset+pageSize].values('pk','email','name', 'memberID', 'academy', 'avatar', 'walletaddress', 'point', 'daypoint', 'weekpoint', 'monthpoint', 'lastdate')
        else:
            userList = User.objects.filter(~Q(is_superuser=True))[offset:offset+pageSize].values('pk','email','name', 'memberID', 'academy', 'avatar', 'walletaddress', 'point', 'daypoint', 'weekpoint', 'monthpoint','lastdate')
        status_code = status.HTTP_200_OK
        response = {
            'status code' : status.HTTP_200_OK,
            'users': userList,
            'totalRecord': userList.count(),
            'pageCount': (userList.count() / pageSize) + 1
        }
        return Response(response, status=status_code)

class CurrencyView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    def get(self, request):
        url = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': '7a8155ce-b1bf-4327-9a3f-11177eb2c01d',
        }
        parameters = {
            'symbol': 'DOT',
            'convert': 'USD'
        }        
        session = Session()
        session.headers.update(headers)
        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)
            response = {
                'status code' : status.HTTP_200_OK,
                'price':data['data']['DOT']['quote']
            }
            status_code = status.HTTP_200_OK
            return Response(response, status=status_code)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            data = json.loads(response.text)
            response={
                'status code' : status.HTTP_400_BAD_REQUEST
            }
            status_code = status.HTTP_400_BAD_REQUEST
            return Response(response, status=status_code)
