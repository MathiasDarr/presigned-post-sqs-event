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
                var url ='https://p7qdv6fqql.execute-api.us-west-2.amazonaws.com/Prod/signedURL'
                var body = {filename:name}
                
                const response = await axios.post(url, body, {
                  headers: {
                      Authorization: this.getIdToken
                    }
                  })

                var data = response.data.presigned 
                
                var object_url = data['url']
                var key = data['fields']['key']
                console.log(object_url+key)


                let form = new FormData()
                Object.keys(data.fields).forEach(key=>form.append(key, data.fields[key]))
                form.append('file', this.file)
                await fetch(data.url, {method:'POST', body: form})
  

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