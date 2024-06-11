"use strict";

// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


app.data = {    
    data: function() {
        return {
            // Complete as you see fit.
            checklists: [],
          
        };
    },
    methods: {
        // Complete as you see fit.

    }
};

app.vue = Vue.createApp(app.data).mount("#app");

app.load_data = function () {
    axios.get(load_checklists_url).then(function (r) {
        app.vue.checklists = r.data.data;
    });
}

app.load_data();