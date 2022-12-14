import math
import time

from pyhtmlgui import PyHtmlView

class DropboxUploadView(PyHtmlView):

    TEMPLATE_STR = '''
        {% if pyview.subject.status == "idle" %}
            <div class="col-md-3" style="text-align: right;padding-top:5px"> </div>
            <div class="col-md-2" style="text-align: right;padding-top:5px"><button class="btn btnfw" onclick="pyview.subject.upload()">Upload to Dropbox</button> </div>
        {% elif pyview.subject.status == "pending" %}
            <div class="col-md-3" style="text-align: right;padding-top:5px"> <p class="h5">Upload pending </p></div>
            <div class="col-md-2" style="text-align: right;padding-top:5px"> </div>
        {% elif pyview.subject.status == "uploading" %}
            <div class="col-md-3" style="text-align: right;padding-top:5px"> <p class="h5">Uploading, {{pyview.subject.progress}}% done      </p> </div>
            <div class="col-md-2" style="padding-top:5px"> <p class="h5"><i>&nbsp;{{pyview.subject.current_upload_file}}&nbsp;</i> </p> </div>
        {% elif pyview.subject.status == "online" %}
            <div class="col-md-3" style="text-align: right;padding-top:5px">
                {% if pyview.subject.last_success != None %}
                    <p class="h5">Last uploaded {{pyview.get_last_success()}} ago</p>
                {% endif %}
            </div>
             <div class="col-md-2" style="text-align: right;padding-top:5px"><button class="btn btnfw" onclick="pyview.subject.upload()">Upload to Dropbox</button>  </div>
        {% else %}
            <div class="col-md-3" style="text-align: right;padding-top:5px"> <p class="h5">{{pyview.subject.status}} </div>
            <div class="col-md-2" style="text-align: right;padding-top:5px"> </div>
        {% endif %} 
    '''
    def get_last_success(self):
        seconds = time.time() - self.subject.last_success
        return self._convert_time(seconds)

    def get_last_failed(self):
        seconds = time.time() - self.subject.last_failed
        return self._convert_time(seconds)

    def _convert_time(self, seconds):
        if seconds < 5:
            return "a few seconds"
        minutes = int(math.ceil(seconds / 60 ))
        if minutes < 2:
            return "%s seconds" % int(seconds)
        hours = int(math.ceil(seconds / 60 / 60 ))
        if hours < 2:
            return "%s minutes" % minutes
        days = int(math.ceil(seconds / 60 / 60 / 24 ))
        if days < 2:
            return "%s hours" % hours
        weeks = int(math.ceil(seconds / 60 / 60 / 24 / 7))
        if weeks < 5:
            return "%s days" % days
        month = int(math.ceil(seconds / 60 / 60 / 24 / 30.416))
        if month < 5:
            return "%s weeks" % weeks
        return "%s month" % month
