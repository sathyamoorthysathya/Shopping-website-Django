from paypal.standard.forms import PayPalPaymentsForm   
from django.shortcuts import render,redirect
from shop.form import CustomUserForm
from . models import *
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout

