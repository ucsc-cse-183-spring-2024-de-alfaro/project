"use strict";

let app = {};

app.data = {    
    data: function() {
        return {
            checklists: [],
            my_value: 0,
            search_query: "",
            search_results: [],
        };
    },
    methods: {
        search: function () {
            let self = this; 
            if (self.search_query.length > 0) {
                axios.get(search_species_url, {params: {q: this.search_query}})
                    .then(function (r) {
                        self.search_results = r.data.results;
                        console.log("Search results;", r.data.results)
                });
            } else {
                self.results = [];
            }
        }
    }
};

app.vue = Vue.createApp(app.data).mount("#app");

app.load_data = function () {
    axios.get(load_checklists_url).then(function (r) {
        app.vue.checklists = r.data.data;
        console.log("Data", r.data.data); 
    });
}

app.load_data();