import time

from pyhtmlgui import Observable
import os




class runSteps():
    def __init__(self):
        self.steps = []
        self.automatic = False
        self.current_step = self.steps[0]
        self.current_step.prepare()
        self.work_q = queue.queue()

    def start(self):
        self.work_q.put(self.current_step)

    def worker(self):
        while True:
            step = self.work_q.get()
            step.run()

    def step_finished_cb(self, step):
        if step.success is True:
            step_index = self.steps.index(step)
            next_step_index = step_index + 1
            if next_step_index < len(self.steps):
                self.current_step = self.steps[next_step_index]
                self.current_step.prepare()
                if self.automatic is True:
                    self.work_q.put(self.current_step)

    def run_current_step(self):
        if self.automatic is False:
            self.work_q.put(self.current_step)


'''

STEPS
prepare folder
write xmp calibration data where available
start new rc instance
create new scene and load images
align images
detect markers and distances
set distances and realign 
clean component naming
export alignments
find camera center
insert and center reconstruction region
correct_colors?
calbulate model
cleanup border region by rotation reconstruction region
clean models and rename finished model
simplify for export
texturize export model
clean and rename export model
save rcproj
export and load xmp files
update calibationdata from xmp data
if export==rcroj
  zip rc_proj
if export==stl,glb,obj
  zip result
if export==gif
  create images
  optimise images
  create gif
  

'''

class RC_Alignment(Observable):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.alignments = []
        self.box_center_correction = [0,0,0]
        self.alignments_csv = parent.get_workfiles_path("alignments.cvs")
        self.rc_proj_file = parent.get_filepath("realityCapture.rcproj")
        self.status = "idle" # failed_ask_abort, repeat, success, failed
        self.alignments_recreated = False


    def run(self):
        self._load_alignments_csv()
        if len(self.alignments) >= 50:
            self.alignments_recreated = False
            self.parent.addlog(["alignments", '%s alignments loaded from cached "%s"' % (len(self.alignments), self.alignments_csv)])
            return True

        result = self._create_alignments()

        #if len(self.alignments) > 50:
        #    self.parent.subtask_xmp.run()

        # xport xmp
        # list cameras with wrong focal distance
        # for each wrong camera:
        #  if has calibration data:
        #    set calibrationdata to fixed
        # write calibration data as xmp
        # if datachanged:
        #  self._create_alignments()
        # if new alignemnts created:
        #  addto calibration
        print("%s alignments loaded" % len(self.alignments))
        return result


    def _create_alignments(self):
        while len(self.alignments) < 50:
            self.clear()
            self._run_rc()
            self._load_alignments_csv()
            if len(self.alignments) >= 50:
                self.alignments_recreated = True
                self.parent.addlog( ["alignments", '%s alignments loaded from "%s"' % (len(self.alignments), self.alignments_csv)])
                return True
            else:
                self.parent.addlog( ["alignments", 'alignments  failed, %s alignments found in "%s", expecting at least 50' % (len(self.alignments), self.alignments_csv)])
                self.set_status("failed_ask_abort")
                while self.status == "failed_ask_abort":
                    time.sleep(1)
                self.clear()
                if self.status != "repeat":
                    break
                self.parent.addlog(["alignments", 'Repeating alignment'])
        self.clear()
        return False


    def _run_rc(self):
        self.parent.addlog(["alignments", 'Starting alignment'])
        cmd = self.parent.get_cmd_start()
        cmd += self.parent.get_cmd_new_scene()
        cmd += '-align '
        cmd += '-detectMarkers "%s\\tmp\\DetectMarkersParams.xml" ' % self.parent.source_path
        for m1m2d in self.parent.subtask_markers.get_available_distances():
            marker1, marker2, distance = m1m2d
            cmd += '-defineDistance "%s" "%s" "%s" "D%s%s" ' % (marker1, marker2, distance, marker1, marker2)
        cmd += '-selectMaximalComponent '
        cmd += '-align '
        cmd += '-renameSelectedComponent "MAIN" '
        cmd += '-selectComponent "Component 0" '
        cmd += '-deleteSelectedComponent '
        cmd += '-selectComponent "MAIN" '
        cmd += '-setReconstructionRegion "%s\\tmp\\box.rcbox" ' % self.parent.source_path
        cmd += '-getLicense "%s" ' % self.parent.pin
        cmd += '-exportRegistration "%s" "%s\\tmp\\exportRegistrationSettings.xml" ' % self.parent.source_path
        cmd += '-save "%s" ' % (self.rc_proj_file)
        cmd += '-quit '
        self.parent.addlog(["alignments", 'Command: %s' % cmd])
        self.parent.run_command(cmd, "load_alignments")

    def _load_alignments_csv(self):
        self.alignments = []
        if os.path.exists(self.alignments_csv):
            self.parent.addlog(["alignments", 'Loading alignments from "%s"' % self.alignments_csv])
            with open(self.alignments_csv, "r") as f:
                for line in f.read().split("\n"):
                    if line.startswith("#") or len(line) < 10:
                        continue
                    al = line.split(",")
                    al = [al[0], float(al[1]), float(al[2]), float(al[3]), None]
                    self.alignments.append(al)
        else:
            self.parent.addlog(["alignments", 'No alignments file exists at "%s"' % self.alignments_csv])

        c_x = (max([x[1] for x in self.alignments]) + min([x[1] for x in self.alignments])) / 2
        c_y = (max([x[2] for x in self.alignments]) + min([x[2] for x in self.alignments])) / 2
        c_z = (max([x[3] for x in self.alignments]) + min([x[3] for x in self.alignments])) / 2

        #avg_x = sum([x[1] for x in self.alignments]) / len(self.alignments)
        #avg_y = sum([x[2] for x in self.alignments]) / len(self.alignments)
        #avg_z = sum([x[3] for x in self.alignments]) / len(self.alignments)
        # print("avg", avg_x, avg_y, avg_z)
        c_z = c_z - (self.parent.box_dimensions[2] / 2)
        self.box_center_correction = [c_x, c_y, c_z]
        self.parent.addlog(["alignments", "Box center corrections: %s,%s,%s" % (c_x, c_y, c_z)])

    def clear(self):
        self.parent.addlog(["alignments", 'Clearing alignments'])
        if os.path.exists(self.alignments_csv):
            os.remove(self.alignments_csv)
        if os.path.exists(self.rc_proj_file):
            os.remove(self.rc_proj_file)
        self.alignments = []
        self.box_center_correction = [0, 0, 0]

    def set_status(self, status):
        if self.status != status:
            self.status = status
            self.notify_observers()
