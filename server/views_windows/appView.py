from pyhtmlgui import PyHtmlView
from views_windows.mainView import MainView
from views_windows.sidebarView import SidebarView


class AppView(PyHtmlView):
    DOM_ELEMENT_CLASS = "AppView container"
    TEMPLATE_STR = '''
        {% if pyview.subject.status == "active"%}
            <div class="row" >
                {{ pyview.sidebarView.render() }}
                {{ pyview.mainView.render()}}
            </div>
        {% else %}
            <div style="width:100%;text-align:center;font-size:3em;padding-top: 20%;color:#aaa">
                {% if  pyview.subject.status == "reboot"%}
                    Reboot in progress, this may take 2-3 minutes
                    <script> setTimeout(function(){ location.reload();}, 130000); </script>
                {% endif %}
                {% if  pyview.subject.status == "shutdown"%}
                    System Shutdown
                {% endif %}
            </div>
        {% endif %}
    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self.mainView = MainView(subject, self)
        self.sidebarView = SidebarView(subject=subject, parent=self)


