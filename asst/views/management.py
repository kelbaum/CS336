from flask import Blueprint, render_template, abort, flash
from flask import request
from asst.auth import require_role
from itertools import *
import traceback
import math
import random
import json
import time

page = Blueprint('management', __name__, template_folder='templates')

@page.route("/",methods=['GET'])
@require_role(['admin','manager'],getrole=True) # Example of requireing a role(and authentication)
def feedback(role):
    return render_template('management/index.html', logged_in=True,role=role)