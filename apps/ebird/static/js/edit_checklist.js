"use strict";

let app = {};

app.data = {    
    data: function() {
        return {
            checklists: []
        };
    },
    methods: {

    }
};

app.vue = Vue.createApp(app.data).mount("#app");

app.load_data = function () {
    axios.get(load_user_checklists_url).then(function (r) {
        app.vue.checklists = r.data.data;
        console.log("user_checklists: ", r.data.data)
    });
}

app.load_data();