import math
from pyhtmlgui import PyHtmlView


class ImageRowView(PyHtmlView):
    TEMPLATE_STR = '''
    <img 
        id="S{{pyview.parent.seg_nr}}_R{{pyview.row_nr}}" 
        style="min-height:{{pyview.parent.parent.img_height}}vw" 
        onerror="this.onerror=null;this.src='/static/images/nophoto.jpg';" 
        src="{{pyview.get_image_source()}}"
    >
    '''

    def __init__(self, subject, parent, row_nr):
        super().__init__(subject, parent)
        self.row_nr = row_nr

    def update(self) -> None:
        if self.is_visible and self.parent is not None:
            js = 'document.getElementById("S%s_R%s").src = "%s"' % (self.parent.seg_nr, self.row_nr, self.get_image_source())
            try:
                self.eval_javascript(js, skip_results=True)
            except:
                pass

    def get_image_source(self):
        return self.parent.parent.get_image_source(self)

    def __eq__(self, other):
        try:
            return self.row_nr == other.row_nr and self.parent.seg_nr == other.parent.seg_nr
        except:
            return False

    def __hash__(self):
        return id(self)


class SegmentView(PyHtmlView):
    TEMPLATE_STR = '''
    {% for image in pyview.images %}
        {{image.render()}}
    {% endfor %}
    '''

    @property
    def DOM_ELEMENT_CLASS(self):
        return "segment segment_%s" % self.seg_nr

    @property
    def DOM_ELEMENT_EXTRAS(self):
        return 'style="width:%s%%;"' % self.parent.segment_width

    def __init__(self, subject, parent, seg_nr):
        super().__init__(subject, parent)
        self.seg_nr = seg_nr
        if self.parent._get_settings_camera_one_position() == "top":
            self.images = [ImageRowView(subject, self, i+1) for i in range(0, self.parent._get_settings_cameras_per_segment() )]
        else:
            self.images = [ImageRowView(subject, self, i) for i in range(self.parent._get_settings_cameras_per_segment(), 0, -1 )]


class ImageCarousel(PyHtmlView):
    TEMPLATE_STR = ''' 
    <div class="controls">
        <div class="col-md-3" ><button class="btn rotate_cw"  onclick='pyview.rotate_cw();' > < </button></div>
        <div class="col-md-3" ><button class="btn rotate_ccw" onclick='pyview.rotate_ccw();'> > </button></div>
        <div class="col-md-3" ><button class="btn zoomin"     onclick='pyview.zoom_in();'   > +   </button></div>
        <div class="col-md-3" ><button class="btn zoomout"    onclick='pyview.zoom_out();'  > -  </button></div>            
        <div class="col-md-3" ><button style="margin-top:10px;padding:6px" class="btn zoomout"    onclick='pyview.switch_type();'  > <i class="fa-solid fa-border-none" style="font-size:1.5em;{% if pyview.image_type == "projection" %}color:#3e8f3e{% endif %}"></i> </button></div>            
    </div>                         
    <div class="carousel">
         {% for segment in pyview.segments %}
              {{segment.render()}}
         {% endfor %}
    </div>
    <div class="numbers">
        {% for segment in pyview.segments %}
          <div class="segment segment_{{segment.seg_nr}}" style="background-color:{{pyview.segment_color(segment.seg_nr)}}; width:{{pyview.segment_width}}%;">
              <div class="number"> - {{segment.seg_nr}} - </div>
          </div>
        {% endfor %}
    </div>
    '''

    def __init__(self, subject, parent):
        super().__init__(subject, parent)
        self.center_segment = 1
        self.segments_shown = 5
        self.image_type = "normal"  # normal|projection
        self.cid = None
        self._segments = []
        self.worker = None


    def _get_settings_camera_one_position(self):
        raise NotImplementedError()

    def _get_settings_camera_rotation(self):
        raise NotImplementedError()

    def _get_settings_segments(self):
        raise NotImplementedError()

    def _get_settings_cameras_per_segment(self):
        raise NotImplementedError()

    def get_image_source(self, imageRowView):
        raise NotImplementedError()

    @property
    def segment_width(self):
        return 100.0/self.segments_shown

    def reset(self):
        self._segments = []
        if self.segments_shown > self._get_settings_segments():
            self.segments_shown = self._get_settings_segments()
        if self.is_visible:
            self.update()

    @property
    def img_height(self):
        if self._get_settings_camera_rotation() in [0, 180]:
            return 100.0 / self.segments_shown / 4 * 3 * 0.79
        else:
            return 100.0 / self.segments_shown / 3 * 4 * 0.79

    @property
    def segments(self):
        max_segments = self._get_settings_segments()
        cid = "%s_%s" % (self.center_segment, self.segments_shown)
        if self.cid == cid:
            return self._segments

        first_segment = math.floor(self.center_segment - ((self.segments_shown - 1) / 2))
        if first_segment < 1:
            first_segment = max_segments + first_segment
        segments = []
        segment = first_segment
        for i in range(self.segments_shown):
            if segment < 1:
                segment = max_segments
            if segment > max_segments:
                segment = 1
            segments.append(int(segment))
            segment = segment + 1
        segments.reverse()

        _segments = []
        for segment_nr in segments:
            s = [s for s in self._segments if s.seg_nr == segment_nr]
            if len(s) == 1:
                s = s[0]
                _segments.append(s)
                self._segments.remove(s)
            else:
                _segments.append(SegmentView(self.subject, self, segment_nr))
        self._segments = _segments
        return _segments

    def segment_color(self, segment):
        s = self._get_settings_segments()
        # colors : 0 - 255 - 0
        colorstep_per_segment = 255 / (s/ 2.0)
        s = abs( segment - (s / 2.0))       # seg8 - 16/2     seg0-8  seg16-8
        c = int(round(255 - (s*colorstep_per_segment),0))
        if c <   0: c = 0
        if c > 255: c = 255
        return "#aaaaaa%02x" % c
        #colors = ["#aaa0", "#aaa2", "#aaa4", "#aaa6", "#aaa8", "#aaaa", "#aaac", "#aaae", "#aaaf", "#aaae", "#aaac", "#aaaa", "#aaa8", "#aaa6", "#aaa4", "#aaa2", ]
        #return colors[segment-1]

    def rotate_cw(self):
        self.center_segment = self.center_segment + 1
        if self.center_segment > self._get_settings_segments():
            self.center_segment = 1
        self.update()

    def rotate_ccw(self):
        self.center_segment = self.center_segment - 1
        if self.center_segment < 1:
            self.center_segment = self._get_settings_segments()
        self.update()

    def zoom_in(self):
        self.segments_shown = self.segments_shown - 1
        if self.segments_shown < 1:
            self.segments_shown = 1
        self.update()

    def zoom_out(self):
        self.segments_shown = self.segments_shown + 1
        if self.segments_shown > self._get_settings_segments():
            self.segments_shown = self._get_settings_segments()
        self.update()

    def switch_type(self):
        self.image_type = "projection" if self.image_type == "normal" else "normal"
        if self.is_visible:
            self.update()

