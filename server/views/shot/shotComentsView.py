from pyhtmlgui import PyHtmlView


class ShotCommentsView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="row">
        <div class="col-md-11" style="font-weight:bold;padding-bottom:10px;">Comments</div>
        <div class="col-md-1" style="font-weight:bold;cursor: pointer"  onclick='pyview.hide()'>
            <a style="text-align: right;float: right;color: gray;">Close</a>
        </div>
    </div>
    <div class="row">
        <div class="col-md-12">
            <textarea style="width: 100%;min-height: 300px;" id="comment_input" onchange='pyview.parent.current_shot.set_comment($("#comment_input").val())'>{{pyview.parent.current_shot.comment}}</textarea>
        </div>
    </div>
    <script>
        {% if pyview.is_hidden %}
            $('#comments_btn').removeClass('top_button_selected');
        {% else %}
            $('#comments_btn').addClass('top_button_selected');
        {% endif %}
    </script>
    '''

    @property
    def DOM_ELEMENT_EXTRAS(self):
        return 'style="display:none;"' if self.is_hidden is True else ""

    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, **kwargs)
        self.is_hidden = True

    def show(self):
        if self.is_hidden is True:
            self.is_hidden = False
            if self.is_visible:
                self.update()

    def hide(self):
        if self.is_hidden is False:
            self.is_hidden = True
            if self.is_visible:
                self.update()

    def toggle(self):
        self.is_hidden = not self.is_hidden
        if self.is_visible:
            self.update()
