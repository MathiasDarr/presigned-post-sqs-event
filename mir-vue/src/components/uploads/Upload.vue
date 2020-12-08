<template>
 <div class="container">
    <div class="large-12 medium-12 small-12 cell">
      <label>File
        <input type="file" id="file" ref="file" v-on:change="onFileChange()"/>
      </label>
     <v-btn small color="primary" v-on:click="submit()">Primary</v-btn>
    </div>
  </div>
</template>


<script>
/* eslint-disable */
import axios from 'axios';
import { mapGetters, mapActions } from "vuex";


export default {
  props: ['files'],
  data () {
    return {
      file: ''
    }
  },

  computed: {
    ...mapGetters(["getEmail", "getIdToken"]),
  },

  methods: {
        


        async fetch_presigned_url(file){
            try{
                
                var name = this.file.name
                console.log(name)
                var url ='https://xjqtewsyu4.execute-api.us-west-2.amazonaws.com/Prod/signedURL'
                var body = {filename:name}
                
                const response = await axios.post(url, body, {
                  headers: {
                      Authorization: this.getIdToken
                    }
                  })
                
                var data = response.data
                var object_url = data['body']

                var parsed_data = JSON.parse(object_url)
                var fields = parsed_data['presigned']['fields']
                
                let form = new FormData()
                Object.keys(fields).forEach(key=>form.append(key, fields[key]))
                form.append('file', this.file)
                var post_url = parsed_data['presigned']['url']
                console.log(post_url)
                // console.log(fields)
                // var options_headers = { "Access-Control-Request-Method" : "POST"}
              
                // let config = {
                //   headers: {
                //     "Access-Control-Request-Method" : "POST"
                //   }
                // }
                // var d = {}

                // await axios.options(post_url, d , config)

                await fetch(parsed_data['presigned']['url'], {method:'POST', body: form})
  

            }catch(err){
                console.log(err)
            }
        },

        async upload_file(){
            await this.fetch_presigned_url(file)
        },

        submit(){
          
          this.upload_file()
        },

        onFileChange(){
          this.file = this.$refs.file.files[0]
          
          
        }
   },
}
</script>