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

export default {
  props: ['files'],
  data () {
    return {
      file: ''
    }
  },
  methods: {

        async fetch_presigned_url(file){
            try{
                // var url = window.__runtime_configuration.apiEndpoint + '/categories'

                var name = this.file.name
                console.log(name)
                var url ='https://cr5nlv4c58.execute-api.us-west-2.amazonaws.com/Prod/signedURL'
                
                var body = {userID:'dakobedbard@gmail.com', filename:name}
                const response = await axios.post(url, body)
                var data = response.data.presigned 
                
                let form = new FormData()
                Object.keys(data.fields).forEach(key=>form.append(key, data.fields[key]))
                form.append('file', this.file)
                await fetch(data.url, {method:'POST', body: form})
                // var parsed_presigned = parsed_body.presigned
  
                // console.log(parsed_presigned)

                // var presignedURL = parsed_presigned.url
                // var signature = parsed_presigned.fields.signature
                // var policy = parsed_presigned.fields.policy
                // var access_key = parsed_presigned.fields.AWSAccessKeyId
                // var key = parsed_presigned.fields.key


                // var body = {
                //   signature:signature,
                //   policy: policy,
                //   AWSAccessKeyId: access_key,
                //   key: key
                // }
                // const formData = new FormData();
                


                // formData.append('key',key)
                // formData.append('AWSAccessKeyId','AKIA2KY4DZB3S7AQRRVH')
                // formData.append('policy',policy)

                // formData.append('signature',signature)
    
                // formData.append('file',this.file)
                // const reader = new FileReader()

                // const xhr = new XMLHttpRequest();
                // xhr.open("OPTIONS", presignedURL)
                // xhr.open("PUT", presignedURL, true);
                
                // xhr.send(formData);
                
                // xhr.onload = function() {
                //   this.status === 204 ? resolve() : reject(this.responseText);
                // };
                
                // var body = {
                //   key:key,
                //   policy: policy,
                //   signature: signature,
                //   AWSAccessKeyId: access_key,
                //   file: file
                // }

              //   fetch(presignedURL,{method:'OPTIONS'})
              //   fetch(presignedURL, {
              //     method: 'POST',
              //     body: formData
              //   })

              //     const config = {
              //   method: "POST",
              //   headers: new Headers({
              //       "Accept": "application/xml"
              //     }),
              //   body: formData,
              // };

              // return fetch(url, config)
              //   .then(response => response.text())
              //   .then((xml) => {
              //     // decode xml and handle response
              //   })
              //   .catch((e) => console.error.bind(console))


                // axios.put(presignedURL, formData)


                

                // axios.put(presignedURL, formData).then(response => {
                //   console.log('response', response)
                // }).catch(error => {
                //   console.log('error', error)
                // })

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