home_button = tk.Button(self.navbar, text='Home', width=size1[0], height=size1[1],
                                command=self.Home)
        home_button.grid(row=0, column=1, sticky='nw')

        exit_button = tk.Button(self.navbar, text='Exit', width=size1[0], height=size1[1],
                                command=self.shut_down)
        exit_button.grid(row=0, column=0, sticky='nw')