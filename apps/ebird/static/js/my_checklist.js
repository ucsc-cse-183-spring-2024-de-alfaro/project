"use strict";

// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


app.data = {    
    data: function() {
        return {
            checklists: [],
            search_query: "",
            search_results: [],
        };
    },
    computed: {
        table_data: function () {
            return this.search_results.length > 0 ? this.search_results : this.checklists;
        }    
    },
    methods: {
       //------ Event Handling ---------------------------------------------------/
       search: function () {
        let self = this; 
        if (self.search_query.length > 0) {
            axios.get(search_species_url, {params: {q: this.search_query}})
                .then(function (r) {
                    self.search_results = r.data.results;
                    console.log("Search results;", r.data.results)
            });
        } else {
            self.search_results = [];
        }
    },

    }
};

app.vue = Vue.createApp(app.data).mount("#app");

app.load_data = function () {
    axios.get(load_my_checklists_url).then(function (r) {
        app.vue.checklists = r.data.data;
    });
}

app.load_data();