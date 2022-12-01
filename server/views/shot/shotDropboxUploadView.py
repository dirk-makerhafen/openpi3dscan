import time

from pyhtmlgui import PyHtmlView

class DropboxUploadView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="col-md-4">
        {% if pyview.subject.status == "idle" %}
            {% if pyview.subject.last_success != None %}
                <p>Last uploaded {{pyview.get_last_success()}} ago</p>
            {% endif %}
            {% if pyview.subject.last_failed != None %}
                <p>Failed to upload {{pyview.get_last_failed()}} ago</p>
            {% endif %}
            <button class="btn" onclick="pyview.subject.sync()">Upload to Dropbox</button>
        {% else %}
            <p>Uploading, {{pyview.subject.current_progress}}% done</p>
            {% if pyview.subject.current_upload_file != "" %}
                <i>{{pyview.subject.current_upload_file}}</i>
            {% else %}
                <p>&nbsp;</p>
            {% endif %}
        {% endif %}
    </div>
    '''
    def get_last_success(self):
        seconds = time.time() - self.subject.last_success
        return self._convert_time(seconds)

    def get_last_failed(self):
        seconds = time.time() - self.subject.last_failed
        return self._convert_time(seconds)

    def _convert_time(self, seconds):
        minutes = int(seconds / 60 )
        if minutes < 2:
            return "%s seconds" % int(seconds)
        hours = int(seconds / 60 / 60 )
        if hours < 2:
            return "%s minutes" % minutes
        days = int(seconds / 60 / 60 / 24 )
        if days < 2:
            return "%s hours" % hours
        weeks = int(seconds / 60 / 60 / 24 / 7)
        if weeks < 5:
            return "%s days" % days
        return "%s weeks" % weeks
