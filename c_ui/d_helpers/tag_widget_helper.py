from c_ui.b_components.b_composite.tag_widget import TagWidget

class TagWidgetHelper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TagWidgetHelper, cls).__new__(cls)
        return cls._instance

    def update_tag_local_value(self, tag_comp_list : list [TagWidget]):
        for tag_comp in tag_comp_list:
            tag_comp.write_to_tag()      

    def reset_tag_local_value(self, tag_comp_list : list [TagWidget]):
        for tag_comp in tag_comp_list:
            tag_comp.tag_model.reset_local_write_value()     

    def reset_tag_remote_value(self, tag_comp_list : list [TagWidget]):
        for tag_comp in tag_comp_list:
            tag_comp.tag_model.reset_remote_value()              
