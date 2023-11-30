// prevents the user from entering bad characters in input that could break the python code :(
    $('input').on('keypress', function (e) {
        if(e.keyCode==13){return true};
        if (e.which < 48 && e.which!=32|| 
          (e.which > 57 && e.which < 65) || 
          (e.which > 90 && e.which < 97) ||
          e.which > 122) {
          e.preventDefault();
      }
      // console.log(e.keyCode)
      });
      
      var wordArrayJson=[];
      // makes a li for available words in signFiles
      
      function test_list()
      {
          
          let ul = document.querySelector(".test_list");
          fetch('static/js/sigmlFiles.json')
          .then(response => response.json())
           .then((data)=>
           {
               data.forEach((e)=>
               {
                  // let word = e.name;
                  let tempjson = {word:e.name};
                  wordArrayJson.push(tempjson);
                   let li=document.createElement("li");
                  //  li.appendChild(document.createTextNode(e.name));
                  li.innerHTML=`<a href="#player" onclick="setSiGMLURL('SignFiles/${e.name}.sigml');" > ${e.name}</a>`
                  ul.appendChild(li);
                  // console.log(e.name);
               });
           });
      
      }
      test_list();
      
      // word array for playing words
      var wordArray=[];
      
      // stops a tag from redirecting
      $('a').click(function(event){
          event.preventDefault();
        });
      
      // stops submit button from submitting the form 
      let form =  document.getElementById('form');
      form.addEventListener('submit', function(event) {
        event.preventDefault();
      });
      
        let sub =  document.getElementById('submit');
        sub.addEventListener('click',()=>
        {
      
          let input =  document.getElementById('text').value;
          console.log("INPUT is ",input);
      
          // ajax request to get the response from flask in json and play the words
            $.ajax({
                url:'/youtube',
                type:'POST',
                data:{text:input},
                success: function(res)
                {
                  convert_json_to_arr(res);
                  play_each_word();
                  display_isl_text(res);
                  display_video();
                },
                error: function(xhr)
                {
                  console.log(xhr);
                }
            });
        });
      
      function display_video()
      {
        let input =  document.getElementById('text').value;
          let video =  document.getElementById('video');
          let id = youtube_parser(input)
          video.src = "https://www.youtube.com/embed/" + id + "?autoplay=1&mute=1";
          console.log("INPUT is ",input);
      }
        // displays isl text 
      function display_isl_text(words)
        {
          
            let p = document.getElementById("isl_text");
            p.textContent="";
            Object.keys(words).forEach(function(key) 
            {
              p.textContent+= words[key]+" ";
            });
        }
        function youtube_parser(url){
          var regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*/;
          var match = url.match(regExp);
          return (match&&match[7].length==11)? match[7] : false;
      }
      // displays currently playing word/letter
        function display_curr_word(word)
        {
            let p = document.querySelector(".curr_word_playing");
            p.textContent=word;
            p.style="color:Red; font-size:24px;font-decoration:bold;";
        }
      
        // displays error message if some error is there
        function display_err_message()
        {
         
          let p = document.querySelector(".curr_word_playing");
          p.textContent="Some error occurred (Probably Sigml file of the word/letter is not proper)";
          p.style="color:Red; font-size:24px;font-decoration:bold;";
        }
      
      // converts the returned  json to array
      function convert_json_to_arr(words)
      {
          wordArray=[];
          console.log("wordArray",words);
          Object.keys(words).forEach(function(key) {
              wordArray.push(words[key]);
          });
          console.log("wordArray",wordArray);
      }
      
      
      // plays each word
      function play_each_word(){
        totalWords = wordArray.length;
        i = 0;
        var int = setInterval(function () {
            if(i == totalWords) {
                if(playerAvailableToPlay) {
                    clearInterval(int);
                    finalHint = $("#inputText").val();
                    $("#textHint").html(finalHint);
                    document.querySelector("#submit").disabled=false;
                }
                else{
                  display_err_message();
                  document.querySelector("#submit").disabled=false;
                }
            } else if(playerAvailableToPlay) {
                    playerAvailableToPlay = false;
                    startPlayer("SignFiles/" + wordArray[i]+".sigml");
                    display_curr_word(wordArray[i]);
                    console.log("CURRENTLY PLAYING",wordArray[i]);
                    document.querySelector("#submit").disabled=true;
                    i++;
                  //   playerAvailableToPlay=true;
                }
               else {
                  let errtext = $(".statusExtra").val(); 
                  console.log("ERROR:- ", "Some error occurred (Probably Sigml file of the word/letter is not proper)");
                  display_err_message();
                  if(errtext.indexOf("invalid") != -1) {
                      playerAvailableToPlay=true;
                      document.querySelector("#submit").disabled=false;
                  }
               }
        }, 1000);
      };
      
      
      // sets the avatarLoaded to true 
      var loadingTout = setInterval(function() {
          if(tuavatarLoaded) {
              // $("#loading").hide();
              clearInterval(loadingTout);
              console.log("Avatar loaded successfully !");
          }
      }, 1500);
      
      