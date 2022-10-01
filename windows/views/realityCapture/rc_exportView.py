from pyhtmlgui import PyHtmlView


class RC_ExportView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-10">
                    <strong class="mb-0">export</strong>
                    <p class="text-muted mb-0">rc_quality=normal</p>
                </div>
                <div class="col-md-2">
                    <div class="custom-control custom-switch">
                    STATUS
                    </div>
                </div>
            </div>
        </div>         
    '''

    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, **kwargs)
