# Import Dependencies
import customtkinter as ctk
import tkinter as tk
import tkcalendar as tkcal
import datetime
import matplotlib
import matplotlib.pyplot as plt

from PIL import Image, ImageTk
from matplotlib.pyplot import style

plt.style.use('tableau-colorblind10')


matplotlib.rc('font', size = 6)

# Set Apperance Mode 
ctk.set_appearance_mode('dark')

class View(ctk.CTk):
     
    # 1280x800
    WIDTH = 1280
    HEIGHT = 800
    FONT = 'Roboto Medium'
    LOG_FONT = 'Consolas'

    MINDATE = datetime.date(2012, 1, 1)
    MAXDATE = datetime.datetime.now()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # Widget States
        self.cal_state = 0
        self.add_reg_checkbox_var = tk.StringVar(self, 'logs')
        
        # Title and Geometry
        self.title('Auto ML Time Series Weather Forecasting')
        self.geometry(f'{View.WIDTH}x{View.HEIGHT}')

        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure(0, weight = 1)

        self.resizable(0, 0)

        self.labels_list = []
        self.checkbox_list = []
        self.forecast_lbls = []

        # Forecast frame size
        self.frame_w = 700
        self.frame_h = 300

        # App Icon
        self.app_icon = tk.PhotoImage(file = 'icons/app_icon_light.png')
        self.iconphoto(False, self.app_icon)

        # Top Frame
        self._top_frame()

        # Main Frame
        self._main_frame()
        self._create_df_frame()
        self._create_extract_frame()
        self._create_overview_frame()
        self._create_plots_frame()

    def main(self):
        self.mainloop()

    # Top Frame
    def _top_frame(self):
        # Photo Images
        divider = Image.open('icons/divider.png')
        icon = Image.open('icons/app_icon_light.png')
        icon_photoimg = ImageTk.PhotoImage(Image.open('icons/app_icon_light.png'))
        div_photoimg = ImageTk.PhotoImage(divider)

        self.top_frame = ctk.CTkFrame(self, 
                                width = View.WIDTH,
                                height = 150,
                                corner_radius = 5)

        # Image Labels
        icon = ctk.CTkLabel(self.top_frame,
                            image = icon_photoimg)
        icon.photo = icon_photoimg

        div = ctk.CTkLabel(self.top_frame,
                           image = div_photoimg,
                           width = 3)
        div.photo = div_photoimg

        top_labels = {'master' : self.top_frame, 
                      'text_font' : (f'{View.FONT}', 14),
                      'width' : 10}

        # Location 
        location_lbl = ctk.CTkLabel(text = 'Location :',**top_labels)
        
        self.location = ctk.CTkEntry(self.top_frame,
                                     placeholder_text = 'Ex. Boston, United States',
                                     width = 170,
                                     height = 30,
                                     corner_radius = 5,
                                     border_width = 1)

        restart_btn = ctk.CTkButton(self.top_frame,
                                    text = 'Create New Dataframe',
                                    text_font = (f'{View.FONT}', 10),
                                    height = 30,
                                    width = 50,
                                    command = self.controller.restart_program)
        
        # Weather Station
        self.weather_station_lbl = ctk.CTkLabel(text = 'Weather Station :', **top_labels)
                                    
        self.top_frame.grid(row = 0, column = 0, stick = 'news')

        icon.place(x = 0, y = 15)
        div.place(x = 150, y = 20)

        location_lbl.place(x = 175, y = 25)
        restart_btn.place(x = 460, y = 25)
        self.location.place(x = 280, y = 25)
        self.weather_station_lbl.place(x = 175, y = 85)

    # Main Frame    
    def _main_frame(self):
        
        # Main Frame
        self.main_frame = ctk.CTkFrame(self,
                                 width = View.WIDTH - 200,
                                 height = 650,
                                 corner_radius = 5)
        self.main_frame.grid(row = 1, column = 0, padx = 10, pady = 10, sticky = 'ew')

        # Widget Atrributes
        date_lbl_attr = {'master' : self.main_frame, 
                         'text_font' : (f'{View.FONT}', 12),
                         'width' : 15}

        date_entry_attr = {'master' : self.main_frame,
                           'placeholder_text' : 'Y - MM - D',
                           'width' : 140,
                           'height' : 40,
                           'corner_radius' : 5,
                           'border_width' : 1 }

        toggle_btn_attr = {'master' : self.main_frame, 
                    'text' : '▼', 
                    'width' : 40, 
                    'height' : 40, 
                    'corner_radius' : 5}

        date_frame_attr = {'master' : self.main_frame,
                           'width' : 310,
                           'height' : 250,
                           'fg_color' : 'gray30',
                           'bg_color' : 'gray20'}
        
        cal_attr = {'mindate' : View.MINDATE,
                    'maxdate' : View.MAXDATE,
                    'font' : (f'{View.FONT}', 12),
                    'date_pattern' : 'Y-mm-dd'}
        
        exit_btn_attr = {'text' : '✕',
                         'text_font' : (f'{View.FONT}', 12),
                         'fg_color' : 'red',
                         'hover_color' : 'darkred',
                         'width' : 10,
                         'height' : 10}

        # Date Labels and Entries
        start_date_lbl = ctk.CTkLabel(text = 'START', **date_lbl_attr)
        start_date_lbl.place(x = 15, y = 18)

        end_date_lbl = ctk.CTkLabel(text = 'END', **date_lbl_attr)
        end_date_lbl.place(x = 265, y = 18)

        # Date Entries
        self.start_date_entry = ctk.CTkEntry(**date_entry_attr)
        self.start_date_entry.place(x = 85, y = 10)

        self.end_date_entry = ctk.CTkEntry(**date_entry_attr)
        self.end_date_entry.place(x = 315, y = 10)
        
        # Toggle TKCalendar Buttons
        self.set_btn = ctk.CTkButton(self.main_frame, 
                                     text = 'Set',
                                     text_font = (f'{View.FONT}', 12),
                                     width = 60,
                                     height = 40,
                                     corner_radius = 5,
                                     command = self.controller.set_date_loc)
        self.set_btn.place(x = 490, y = 10)

        # Create Toggle Functions
        # Toggle Start Calendar
        def toggle_start_cal(self):
            self.cal_state = 1
            print(self.cal_state)
            self.start_date_frame = ctk.CTkFrame(**date_frame_attr)
            self.start_date = tkcal.Calendar(master = self.start_date_frame, **cal_attr)

            start_exit_btn = ctk.CTkButton(master = self.start_date_frame, 
                                            command = lambda: exit_frame(self, self.start_date_frame),
                                            **exit_btn_attr)
            
            self.start_date.place(x = 0, y = 27)
            self.start_date_frame.place(x = 0, y = 50)
            start_exit_btn.place(x = 275, y = 1)

        # Toggle End Calendar
        def toggle_end_cal(self):
            self.cal_state = 1
            print(self.cal_state)
            self.end_date_frame = ctk.CTkFrame(**date_frame_attr)
            self.end_date = tkcal.Calendar(master = self.end_date_frame, **cal_attr)

            end_exit_btn = ctk.CTkButton(master = self.end_date_frame,
                                         command = lambda: exit_frame(self, self.end_date_frame),
                                         **exit_btn_attr)
            
            self.end_date.place(x = 0, y = 27)
            self.end_date_frame.place(x = 315, y = 50)
            end_exit_btn.place(x = 275, y = 1)
        
        # Exit Calendar
        def exit_frame(self, widget):
            self.cal_state = 0
            print(self.cal_state)
            widget.destroy()

        # Toggle TKCalendar Buttons
        self.start_cal_btn = ctk.CTkButton(command = lambda: toggle_start_cal(self), **toggle_btn_attr)
        self.start_cal_btn.place(x = 205, y = 10)

        self.end_cal_btn = ctk.CTkButton(command = lambda: toggle_end_cal(self), **toggle_btn_attr)
        self.end_cal_btn.place(x = 435, y = 10)
    
    def _create_df_frame(self):
        self.df_frame = ctk.CTkFrame(self.main_frame, 
                                     width = 550,
                                     height = 580,
                                     corner_radius = 5)
        self.df_frame.place(x = 10, y = 60)

    def _create_extract_frame(self):
        self.extract_frame = ctk.CTkFrame(self.main_frame, 
                                          width = 550,
                                          height = 580,
                                          corner_radius = 5)
        self.extract_frame.place(x = 10, y = 60)

        self.extract_btn = ctk.CTkButton(self.extract_frame,
                                        text = 'Extract Data',
                                        text_font = (f'{View.FONT}', 14),
                                        width = 150,
                                        height = 40,
                                        corner_radius = 10,
                                        command = self.controller.show_weather_df,
                                        state = 'disabled')
        self.extract_btn.place(x = 190, y = 290)

    #==============# Data Statistics #==============#

    # Base Frame
    def _create_overview_frame(self):
        self.profile_frame_lbl = ctk.CTkLabel(self.main_frame,
                                                text = 'Overview',
                                                text_font = (f'{View.FONT}', 24))
        self.profile_frame_lbl.place(x = 570, y = 15)
        self.profile_frame = ctk.CTkFrame(self.main_frame,
                                          width = 675,
                                          height = 215,
                                          corner_radius = 5)
        self.profile_frame.place(x = 575, y = 60)

    # Option Menu to switch from Dataset Stats and Feature Stats
    def overview_option_menu(self):
        self.overview_optionmenu = ctk.CTkOptionMenu(self.main_frame,
                                                     text_font = (f'{View.FONT}',12),
                                                     values = ['Dataset Statistics', 'Feature Statistics'],
                                                     command = self.controller.overview_callback)
        self.overview_optionmenu.place(x = 1080, y = 15)

    # Dataset Statistics
    def df_stats_widgets(self, weather_overview:dict):
        # Frame
        self.dataset_stats_frame = ctk.CTkFrame(self.main_frame,
                                                width = 675,
                                                height = 215,
                                                corner_radius = 5)
        self.dataset_stats_frame.place(x = 575, y = 60)

        # Create labels
        i = 1
        for key, val in weather_overview.items():
            # Keys 
            ctk.CTkLabel(self.dataset_stats_frame,
                         text = key,
                         text_font = (f'{View.FONT}', 11)).place(x = 50, y = 26*i)
            # Values
            ctk.CTkLabel(self.dataset_stats_frame,
                         text = val,
                         text_font = (f'{View.FONT}', 11)).place(x = 500, y = 26*i)
            i+=1
    
    # Feature Statistics
    def feature_stats_widgets(self, weather_df):
        # Frame
        self.feature_stats_frame = ctk.CTkFrame(self.main_frame,
                                                width = 675, 
                                                height = 215, 
                                                corner_radius = 5)
        self.feature_stats_frame.place(x = 575, y = 60)

        # Option menu for different features
        self.feature_option_menu = ctk.CTkOptionMenu(self.feature_stats_frame,
                                                     text_font = (f'{View.FONT}', 12),
                                                     values = list(weather_df.columns),
                                                     command = self.controller.feature_option_callback)
        self.feature_option_menu.place(x = 10, y = 10)

        # Seasonal Decompose Feature
        self.decompose_btn = ctk.CTkButton(self.feature_stats_frame, 
                                           text = 'Decompose',
                                           text_font = (f'{View.FONT}', 11),
                                           command = self.controller.display_seasonal_decomposition)
        self.decompose_btn.place(x = 160, y = 10)

        # Create Model
        self.create_model_btn = ctk.CTkButton(self.feature_stats_frame,
                                                    text = 'Create Model',
                                                    text_font = (f'{View.FONT}', 11),
                                                    command = self.controller.neuralprophet_modelling_frame)
        self.create_model_btn.place(x = 525, y = 10)

    # Updates labels when switching betweeen features in option menu
    def feature_stats_labels(self, weather_df_described):

        # Destroy pre-existing labels
        if len(self.labels_list) != 0:
            for label in self.labels_list:
                label.destroy()
            self.labels_list.clear()

        self.feature_labels_frame = ctk.CTkFrame(self.feature_stats_frame,
                                            width = 900,
                                            height = 500,
                                            corner_radius = 5,
                                            fg_color = '#343638')
        self.feature_labels_frame.place(x = 30, y = 100)

        # Configure rows and columns (8x2; Col x Row)
        for col in range(8):
            self.feature_labels_frame.grid_columnconfigure(col, weight = 1)
            for row in range(2):
                self.feature_labels_frame.grid_rowconfigure(row, weight = 1)

        # Prints index values on the first row and values on the second row
        for row in range(2):
            for col in range(8):
                values = weather_df_described.index if row == 0 else weather_df_described.values
                label = ctk.CTkLabel(self.feature_labels_frame,
                                text = values[col],
                                width = 50,
                                text_font = (f'{View.FONT}', 11))
                label.grid(row = row, column = col, padx = (16, 10))
                self.labels_list.append(label)
            
    #==============# Seasonal Decomposition #==============#

    # Base Frame
    def _create_plots_frame(self):
        self.plot_frame = ctk.CTkFrame(self.main_frame,
                                          width = 675,
                                          height = 350,
                                          corner_radius = 5)
        self.plot_frame.place(x = 575, y = 290)

    def plot_feature_widgets(self):
        # Canvas
        self.canvas_frame = ctk.CTkFrame(self.plot_frame,
                                         width = 640,
                                         height = 312,
                                         corner_radius = 5)
        self.canvas_frame.place(x = 20, y = 20)

    #==============# Prophet Modelling  #==============#

    def _modelling_frame(self, weather_df):
        # Prophet Model Frame
        self.modelling_frame = ctk.CTkFrame(self, 
                                            width = View.WIDTH - 200,
                                            height = 650,
                                            corner_radius = 5)
        self.modelling_frame.grid(row = 1, column = 0, padx = 10, pady = 10, sticky = 'ew') 

        # Target Feature 
        target_feature_lbl = ctk.CTkLabel(self.modelling_frame, 
                                               text = 'Target Feature : ',
                                               text_font = (f'{View.FONT}', 14))
        target_feature_lbl.place(x = 40, y = 40)

        self.target_option_menu = ctk.CTkOptionMenu(self.modelling_frame,
                                                     width = 150,
                                                     text_font = (f'{View.FONT}', 13),
                                                     values = ['tavg', 'tmin', 'tmax'])
        self.target_option_menu.place(x = 200, y = 40)
        
        self.confirm_target_btn = ctk.CTkButton(self.modelling_frame,
                                                text = 'Target: Not Set',
                                                text_font = (f'{View.FONT}', 13),
                                                command = self.controller.set_target_feature,
                                                fg_color = '#E41E3F',
                                                hover_color = '#8C1E3F')
        self.confirm_target_btn.place(x = 360, y = 40)

        # Additional Regressors
        add_reg_lbl = ctk.CTkLabel(self.modelling_frame,
                                        text = 'Additional Regressors',
                                        text_font = (f'{View.FONT}', 14))
        add_reg_lbl.place(x = 40, y = 100)

        self.add_reg_checkbox = ctk.CTkCheckBox(self.modelling_frame,
                                                text = '',
                                                onvalue = 'on',
                                                offvalue = 'off',
                                                variable = self.add_reg_checkbox_var,
                                                command = self.controller.get_regressors,
                                                state = tk.DISABLED)
        self.add_reg_checkbox.place(x = 250, y = 103)

        self.regressors_frame = ctk.CTkFrame(self.modelling_frame,
                                            width = 480,
                                            height = 380,
                                            fg_color = '#2A2D2E',
                                            corner_radius = 5)
        self.regressors_frame.place(x = 20, y = 155)

        self.forecast_test_btn = ctk.CTkButton(self.modelling_frame,
                                       text = 'Fit Train Data',
                                       text_font = (f'{View.FONT}', 14),
                                       width = 220,
                                       height = 50,
                                       command = self.controller.forecast_test,
                                       state = 'disabled')
        self.forecast_test_btn.place(x = 40, y = 565) # y = 565

        self.forecast_future_btn = ctk.CTkButton(self.modelling_frame,
                                                 text = 'Fit DataFrame',
                                                 text_font = (f'{View.FONT}', 14),
                                                 width = 220,
                                                 height = 50,
                                                 command = self.controller.forecast_future,
                                                 state = 'disabled')
        self.forecast_future_btn.place(x = 290, y = 565) # y = 565

        # self.year_entry = ctk.CTkEntry(self.modelling_frame,
        #                                placeholder_text = 'Number of years in the future to forecast',
        #                                corner_radius = 5,
        #                                border_width = 1,
        #                                width = 170,
        #                                height = 30,
        #                                state = tk.DISABLED)
        # self.year_entry.place(x = 650, y = 40)

    def temporary_regressor_widgets(self):
        self.temp_regressors_frame = ctk.CTkFrame(self.modelling_frame,
                                                  width = 480,
                                                  height = 380,
                                                  fg_color = '#2A2D2E',
                                                  corner_radius = 5)
        self.temp_regressors_frame.place(x = 40, y = 155)

        self.temp_regressors_info = ctk.CTkLabel(self.temp_regressors_frame,
                                                 text = '- Tick the box to use additional regressors -',
                                                 text_font = (f'{View.FONT}', 12))
        self.temp_regressors_info.place(x = (480/2) - 170, y = (400/2) - 20)
    
    def _regressors_check_boxes(self, train_data):
        # Checkbox frame
        self.checkbox_frame = ctk.CTkFrame(self.regressors_frame,
                                           width = 400,
                                           height = 300,
                                           fg_color = '#2A2D2E',
                                           corner_radius = 5)
        self.checkbox_frame.place(x = 100, y = 20)
        
        # Set rows 
        for row in range(len(train_data)-1):
            self.checkbox_frame.grid_columnconfigure(row, weight = 1)
        
        # Create checkboxes
        for idx in range(len(train_data)):
            checkbox = ctk.CTkCheckBox(self.checkbox_frame,
                                       text = train_data[idx],
                                       text_font = (f'{View.FONT}', 14),
                                       onvalue = 'on',
                                       offvalue = 'off',
                                       command = self.controller.add_regressor)
            checkbox.grid(row = idx, column = 0, pady = (0, 25), sticky = 'W')
            self.checkbox_list.append(checkbox)

    def _temp_forecast_results(self):
        self.temp_forecast_results = ctk.CTkFrame(self.modelling_frame,
                                             width = self.frame_w,
                                             height = self.frame_h,
                                             corner_radius = 5)
        self.temp_forecast_results.place(x = 540, y = 330)

        self.forecast_btn = ctk.CTkButton(self.temp_forecast_results,
                                         text = 'Generate Forecast',
                                         text_font = (f'{View.FONT}', 14),
                                         width = 220,
                                         height = 50,
                                         command = lambda: self.controller.predict(self.controller.btn_val),
                                         state = 'disabled')
        self.forecast_btn.place(x = (self.frame_w/2)-95, y = (self.frame_h/2)-20)
    
    def _forecast_results_widgets(self, forecast_start, forecast_end):
        self.get_pred_entry = ctk.CTkEntry(self.temp_forecast_results,
                                           placeholder_text = 'Y - MM -DD',
                                           width = 170,
                                           height = 40,
                                           corner_radius = 8,
                                           border_width = 1)
        self.get_pred_entry.place(x = 380, y = 10)

        self.forecast_info = ctk.CTkLabel(self.temp_forecast_results,
                                          text = f'- Enter a date between ({forecast_start}) and ({forecast_end}) to view prediction -',
                                          text_font = (f'{View.FONT}', 11))
        self.forecast_info.place(x = (self.frame_w/2)-240, y = (self.frame_h/2))
        
        self.set_date_pred = ctk.CTkButton(self.temp_forecast_results,
                                           text = 'Set',
                                           text_font = (f'{View.FONT}', 12),
                                           height = 40,
                                           width = 130,
                                           command = self.controller.display_pred_actual)
        self.set_date_pred.place(x = 560, y = 10)
    
    def _forecast_results_labels(self, prediction, date, validation = None, metrics = None):

        if len(self.forecast_lbls) > 0:
            for widget in self.forecast_lbls:
                widget.destroy()

        self.prediction_lbl = ctk.CTkLabel(self.temp_forecast_results,
                                           text = prediction,
                                           text_font = (f'{View.FONT}', 90))
        self.prediction_lbl.place(x = 40, y = 140)
        
        self.date_lbl = ctk.CTkLabel(self.temp_forecast_results,
                                     text = date,
                                     text_font = (f'{View.FONT}', 14))
        self.date_lbl.place(x = 35, y = 100)

        self.validation_lbl = ctk.CTkLabel(self.temp_forecast_results,
                                           text = validation,
                                           text_font = (f'{View.FONT}', 12))
        self.validation_lbl.place(x = 200, y = 100)

        self.metrics_frame = ctk.CTkFrame(self.temp_forecast_results,
                                          width = 50,
                                          height = 50,
                                          fg_color = '#343638')
        self.metrics_frame.place(x = 400, y = 180)

        for col in range(len(metrics)-1):
            self.metrics_frame.grid_columnconfigure(col, weight = 0)
            for row in range(len(metrics)):
                self.metrics_frame.grid_rowconfigure(row, weight = 0)

        for row in range(len(metrics)):
            for col in range(len(metrics)-1):
                values = list(metrics.keys()) if col == 0 else list(metrics.values())
                self.metric_lbl = ctk.CTkLabel(self.metrics_frame,
                                                text = values[row],
                                                text_font = (f'{View.FONT}', 10))
                self.metric_lbl.grid(row = row, column = col, sticky = 'w')

        self.forecast_lbls = [self.prediction_lbl, self.date_lbl, self.validation_lbl, self.metrics_frame]

        # i = 0
        # for key, val in metrics.items():
        #     i+=10
        #     self.metric_lbl = ctk.CTkLabel(self.metrics_frame,
        #                                    text = f'{key} : {val}',
        #                                    text_font = (f'{View.FONT}', 10))
        #     self.metric_lbl.grid(row = )
            # self.forecast_lbls.append(self.metric_lbl)

    def _temp_train_results(self):
        log_relative_size = 40
        self.train_frame = ctk.CTkFrame(self.modelling_frame,
                                          width = self.frame_w,
                                          height = self.frame_h, 
                                          corner_radius = 5)
        self.train_frame.place(x = 540, y = 15)

        self.train_log = ctk.CTkTextbox(self.train_frame, 
                                        width = self.frame_w,
                                        height = self.frame_h-log_relative_size,
                                        text_font = (f'{View.LOG_FONT}', 10),
                                        fg_color = '#202428',
                                        state = 'disabled')
        self.train_log.place(x = 0, y = 45)

    # Custom segmented button for switching between tabs
    def _results_tabs(self):
        self.tab_btn_frame = ctk.CTkFrame(self.train_frame,
                                          width = self.frame_w - 490,
                                          height = 30,
                                          corner_radius = 15)
        self.tab_btn_frame.place(x = (self.frame_w/2)-93, y = 10)

        tab_btn_attr = {'master' : self.tab_btn_frame,
                        'text_font' : (f'{View.FONT}', 12),
                        'width' : 100,
                        'height' : 30,
                        'fg_color' : '#25292E'}

        self.log_btn = ctk.CTkButton(text = 'Logs',
                                     state = 'disabled', 
                                     command = lambda: self.controller.switch_tab('logs'),
                                     **tab_btn_attr)
        self.log_btn.place(x = 0, y = 0)

        self.plots_btn = ctk.CTkButton(text = 'Plots',
                                       state = 'disabled',
                                       command = lambda: self.controller.switch_tab('plots'),
                                       **tab_btn_attr)
        self.plots_btn.place(x = 110, y = 0)
    
    def _result_plots_tab(self):
        results_frame_attr = {'width' : self.frame_w,
                              'height' : self.frame_h-40,
                              'corner_radius' : 5}

        self.result_plots_base = ctk.CTkFrame(master = self.train_frame, **results_frame_attr)
        self.result_plots_base.place(x = 0, y = 45)

        self.forecast_canvas_frame = ctk.CTkFrame(master = self.result_plots_base, **results_frame_attr)
        self.forecast_canvas_frame.place(x = 0, y = 0)
