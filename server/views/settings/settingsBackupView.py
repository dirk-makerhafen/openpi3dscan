from pyhtmlgui import PyHtmlView, ObservableListView


class SettingsBackupView(PyHtmlView):
    TEMPLATE_STR = '''
    <div class="Backups">
        <div class="row justify-content-center" style="width:100%">
            <div class="col-md-12">
                <div class="list-group mb-5 shadow">
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-12 h3" style="border-bottom: 1px solid lightgray;">Backups</div>
                        </div>
                    </div>
                    <div class="list-group-item">
                        <div class="row align-items-center">
                            <div class="col-md-10">
                                <strong class="mb-0">Create Backup</strong>
                                <p class="text-muted mb-0">Download a backup of all settings for this scanner</p>
                            </div>
                            <div class="col-md-2">
                                <a href="/settings_backup">Download</a>
                            </div>
                        </div>
                    </div>                                
                </div>
            </div>   
        </div>
    </div>
    '''
    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, **kwargs)


