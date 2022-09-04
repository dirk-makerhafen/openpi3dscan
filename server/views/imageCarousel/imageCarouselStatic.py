from views.imageCarousel.imageCarousel import ImageCarousel
from app.devices.devices import DevicesInstance


class ImageCarouselStatic(ImageCarousel):
    DOM_ELEMENT_CLASS = "ImageCarousel"

    def __init__(self, subject, parent):
        super().__init__(subject, parent)

    def get_image_source(self, imageRowView):
        image_mode = "normal" if self.segments_shown == 1 else "preview"
        device_id = 100 + ((imageRowView.parent.seg_nr - 1) * 7) +  imageRowView.row_nr
        return "/shots/%s/%s/%s/%s.jpg" % (self.parent.current_shot.shot_id, image_mode, self.image_type, device_id )
