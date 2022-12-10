import os, time, glob
import shutil
from multiprocessing.pool import ThreadPool

from app_windows.realityCapture.genericTask import GenericTask


box_rcbox = '''
<ReconstructionRegion globalCoordinateSystem="NONE" globalCoordinateSystemWkt="NONE" globalCoordinateSystemName="NONE"
   isGeoreferenced="0" isLatLon="0" yawPitchRoll="0 -0 -0" widthHeightDepth="%s %s %s">
  <Header magic="5395016" version="2"/>
  <CentreEuclid centre="0 0 %s"/>
  <Residual R="1 0 0 0 1 0 0 0 1" t="0 0 0" s="1" ownerId="{65DB1F2C-807B-4520-937D-FB2D78C646D9}"/>
</ReconstructionRegion>
'''
DetectMarkersParams_xml = '''
<Configuration id="{8D21413B-0848-49A9-BF6E-8EBCCA356BC7}">
  <entry key="minMarkerMeasurements" value="0x4"/>
  <entry key="generateMarkersPaperSize" value="0"/>
  <entry key="generateMarkersMarkersPerPage" value="0x4"/>
  <entry key="generateMarkersCount" value="0x4"/>
  <entry key="imageLayer" value="geometry"/>
  <entry key="markerType" value="Circular1x12Bit"/>
</Configuration>
'''
ExportRegistrationSettings_xml = '''
<Configuration id="{2D5793BC-A65D-4318-A1B9-A05044608385}">
  <entry key="calexTrans" value="1"/>
  <entry key="calexHasDisabled" value="0x0"/>
  <entry key="MvsExportScaleZ" value="1.0"/>
  <entry key="MvsExportIsGeoreferenced" value="0x0"/>
  <entry key="MvsExportIsModelCoordinates" value="0"/>
  <entry key="MvsExportScaleY" value="1.0"/>
  <entry key="MvsExportScaleX" value="1.0"/>
  <entry key="MvsExportRotationY" value="0.0"/>
  <entry key="MvsExportcoordinatesystemtype" value="0"/>
  <entry key="MvsExportNormalFlipZ" value="false"/>
  <entry key="MvsExportRotationX" value="0.0"/>
  <entry key="hasCalexFilePath" value="1"/>
  <entry key="MvsExportNormalFlipY" value="false"/>
  <entry key="MvsExportNormalSpace" value="Mikktspace"/>
  <entry key="calexHasUndistort" value="-1"/>
  <entry key="MvsExportNormalFlipX" value="false"/>
  <entry key="MvsExportRotationZ" value="0.0"/>
  <entry key="calexFileFormat" value="Comma-separated, Name, X, Y, Z, Omega, Phi, Kappa"/>
  <entry key="MvsExportMoveZ" value="0.0"/>
  <entry key="calexFileFormatId" value="{B3EE1544-1D64-4C22-A47D-FC9F78C107B7}"/>
  <entry key="hasCalexFileName" value="1"/>
  <entry key="calexHasImageExport" value="-1"/>
  <entry key="MvsExportMoveX" value="0.0"/>
  <entry key="MvsExportNormalRange" value="ZeroToOne"/>
  <entry key="MvsExportMoveY" value="0.0"/>
</Configuration>
'''
XMPSettings_xml = '''
<Configuration id="{EC40D990-B2AF-42A4-9637-1208A0FD1322}">
  <entry key="xmpMerge" value="true"/>
  <entry key="xmpExGps" value="true"/>
  <entry key="xmpFlags" value="true"/>
  <entry key="xmpCalibGroups" value="true"/>
  <entry key="xmpCamera" value="1"/>
  <entry key="xmpRig" value="true"/>
</Configuration>
'''
groundPlaneImport_xml = '''
<Configuration id="{65E79B42-7042-4A81-B68D-0F835D913191}">
  <entry key="gcpuPosXl" value="0.05"/>
  <entry key="csvGCIgn" value="false"/>
  <entry key="gcpuPosZl" value="0.1"/>
  <entry key="gcpTmode" value="0x1"/>
  <entry key="CoordinateSystemGcpType" value="local:1 - Euclidean"/>
  <entry key="CoordinateSystemGcp" value="+proj=geocent +ellps=WGS84 +no_defs"/>
  <entry key="gcpLogFileFormat" value="{95EB0F80-BF22-4C4E-9DD9-C04C6C95E933}"/>
  <entry key="gcpuPosYl" value="0.05"/>
  <entry key="csvGCSep" value="0"/>
</Configuration>
'''




class PrepareFolder(GenericTask):
    def __init__(self, rc_job):
        super().__init__(rc_job)

    def run(self):
        self.set_status("active")
        if not os.path.exists(self.rc_job.workingdir):
            os.mkdir(self.rc_job.workingdir)
            self.log.append("Cache directory created %s" % self.rc_job.workingdir)
        else:
            self.log.append("Cache found at %s" % self.rc_job.workingdir)

        with open(os.path.join(self.rc_job.workingdir, "last_usage"), "w") as f:
            f.write("%s" % int(time.time()))

        if not os.path.exists(os.path.join(self.rc_job.workingdir, "tmp")):
            os.mkdir(os.path.join(self.rc_job.workingdir, "tmp"))
        if not os.path.exists(os.path.join(self.rc_job.workingdir, self.rc_job.export_foldername)):
            os.mkdir(os.path.join(self.rc_job.workingdir, self.rc_job.export_foldername))

        with open(self.get_path("DetectMarkersParams.xml"), "w") as f:
            f.write(DetectMarkersParams_xml)
        with open(self.get_path("box.rcbox"), "w") as f:
            f.write(box_rcbox  % (round(self.rc_job.box_dimensions[0], 4), round(self.rc_job.box_dimensions[1], 4), round(self.rc_job.box_dimensions[2], 4), round(self.rc_job.box_dimensions[2]/2, 4)))
        with open(self.get_path("exportRegistrationSettings.xml"), "w") as f:
            f.write(ExportRegistrationSettings_xml)
        with open(self.get_path("xmp_settings.xml"), "w") as f:
            f.write(XMPSettings_xml)
        with open(self.get_path("groundPlaneImport.xml"), "w") as f:
            f.write(groundPlaneImport_xml)

        if len(self.rc_job.license_data) > 0:
            with open(self.get_path("license.rclicense"), "w") as f:
                f.write(self.rc_job.license_data)

        if self.rc_job.source_ip is None:
            if not os.path.exists(os.path.join(self.rc_job.workingdir, "images")):
                os.mkdir(os.path.join(self.rc_job.workingdir, "images"))
            existed_in_cache = True
            for imgtype in ["normal", "projection"]:
                if not os.path.exists(os.path.join(self.rc_job.workingdir, "images", imgtype)):
                    existed_in_cache = False
                    if os.path.exists(os.path.join(self.rc_job.source_dir, "images", imgtype)):
                        shutil.copytree(os.path.join(self.rc_job.source_dir, "images", imgtype), os.path.join(self.rc_job.workingdir, "images", imgtype))
                    elif os.path.exists(os.path.join(self.rc_job.source_dir, imgtype)):
                        shutil.copytree(os.path.join(self.rc_job.source_dir, imgtype), os.path.join(self.rc_job.workingdir, "images", imgtype))
            nr_of_images = len(glob.glob(os.path.join(self.rc_job.workingdir, "images", "*", "*.jpg")))
            if nr_of_images == 0:
                self.log.append("No images copied from %s, failed" % self.rc_job.source_dir)
                self.set_status("failed")
            else:
                if existed_in_cache is False:
                    self.log.append("%s images copied to cache" % (nr_of_images))
                else:
                    self.log.append("%s images exist in cache" % (nr_of_images))
                self.set_status("success")
        else:
            self.set_status("success")