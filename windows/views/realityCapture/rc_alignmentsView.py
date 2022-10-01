from pyhtmlgui import PyHtmlView


class RC_AlignmentsView(PyHtmlView):
    TEMPLATE_STR = '''
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-10">
                    <strong class="mb-0">Alignments</strong>
                    <p class="text-muted mb-0">Find camera alignments</p>
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
