from views.images.imagesView import ImagesView


class ImagesStaticView(ImagesView):
    DOM_ELEMENT_CLASS = "ImageCarousel"

    def __init__(self, subject, parent):
        self._on_subject_updated = None
        super().__init__(subject, parent)

    def _get_settings_camera_one_position(self):
        return self.subject.meta_camera_one_position

    def _get_first_camera_number(self):
        return self.subject.meta_first_camera_number

    def _get_settings_camera_rotation(self):
        return self.subject.meta_rotation

    def _get_settings_segments(self):
        return self.subject.meta_max_segments

    def _get_settings_cameras_per_segment(self):
        return self.subject.meta_max_rows

    def get_image_source(self, imageRowView):
        image_mode = "normal" if self.segments_shown == 1 else "preview"
        #device_id = 100 + ((imageRowView.parent.seg_nr - 1) * self.ss.cameras_per_segment) + imageRowView.row_nr
        fname = "seg%s-cam%s-%s.jpg" % (imageRowView.parent.seg_nr, imageRowView.row_nr, self.image_type[0])
        return "/shots/%s/%s/%s/%s" % (self.subject.shot_id, image_mode, self.image_type, fname)
