from app.settings.settings import SettingsInstance
from views.imageCarousel.imageCarousel import ImageCarousel


class ImageCarouselStatic(ImageCarousel):
    DOM_ELEMENT_CLASS = "ImageCarousel"

    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self.ss = SettingsInstance().settingsScanner

    def get_image_source(self, imageRowView):
        image_mode = "normal" if self.segments_shown == 1 else "preview"
        #device_id = 100 + ((imageRowView.parent.seg_nr - 1) * self.ss.cameras_per_segment) + imageRowView.row_nr
        fname = "seg%s-cam%s-%s.jpg" % (imageRowView.parent.seg_nr, imageRowView.row_nr, self.image_type[0])
        return "/shots/%s/%s/%s/%s" % (self.parent.current_shot.shot_id, image_mode, self.image_type, fname)
