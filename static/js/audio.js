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
  
  document.addEventListener("DOMContentLoaded", function() {
    test_list();
  });
  
  document.addEventListener("DOMContentLoaded", function() {
    function startsWithNumber(str) {
      return /^\d/.test(str);
    }
  
    function test_list() {
      let ul = document.querySelector(".numericDigits");
  
      console.log("test_list function is called");
  
      fetch('static/js/sigmlFiles.json')
        .then(response => response.json())
        .then((data) => {
          console.log("Fetched data:", data);
  
          data.forEach((e) => {
            console.log("Processing:", e.name);
  
            if (startsWithNumber(e.name)) {
              console.log("Creating button for:", e.name);
  
              let button = document.createElement("button");
              let li = document.createElement("li");
  
              button.innerHTML = `<a href="#player" onclick="setSiGMLURL('SignFiles/${e.name}.sigml');">${e.name}</a>`;
              li.appendChild(button);
              ul.appendChild(li);
            }
          });
        })
        .catch(error => {
          console.error("Error fetching JSON:", error);
        });
    }
  
    test_list();
  });
  
  function generateContent(word) {
    return `<a href="#player" onclick="setSiGMLURL('SignFiles/${word}.sigml');">${word}</a>`;
  }
  
  async function generateAlphabetList(className) {
    try {
        const ul = document.querySelector(`.${className}`);
        const response = await fetch('static/js/sigmlFiles.json');
        const data = await response.json();
  
        data.forEach((e) => {
            if (e.name.toLowerCase().startsWith(className.toLowerCase())) {
                const li = document.createElement("li");
                const button = document.createElement("button");
                button.innerHTML = generateContent(e.name);
                ul.appendChild(li);
                li.appendChild(button)
            }
        });
    } catch (error) {
        console.error('Error fetching or processing data:', error);
    }
  }
  
  document.addEventListener('DOMContentLoaded', async function () {
    // Get the accordion container
    const accordionContainer = document.getElementById('alphabetAccordion');
  
    // Generate accordion items for each letter
    for (let i = 65; i <= 90; i++) {
        const letter = String.fromCharCode(i);
        const accordionItem = generateAccordionItem(letter);
        accordionContainer.innerHTML += accordionItem;
  
        // Example usage for each letter, appending to the corresponding accordion item
        await generateAlphabetList(letter);
    }
  });
  
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
  
      var output = document.getElementById("output");
      // get action element reference
      var action = document.getElementById("action");
      // new speech recognition object
      var SpeechRecognition = SpeechRecognition || webkitSpeechRecognition;
      var recognition = new SpeechRecognition();

      // This runs when the speech recognition service starts
      recognition.onstart = function() {
        action.innerHTML = "<small>listening, please speak...</small>";
    };
    
    recognition.onspeechend = function() {
        action.innerHTML = "<small>stopped listening, hope you are done...</small>";
        recognition.stop();
    }
  
    // This runs when the speech recognition service returns result
    recognition.onresult = function(event) {
        var transcript = event.results[0][0].transcript;
        //var confidence = event.results[0][0].confidence;
        output.innerHTML = "<b>Text:</b> " + transcript;
        output.classList.remove("hide");
        $.ajax({
            url:'/audio_to_text',
            type:'POST',
            data:{text:transcript},
            success: function(res)
            {
              convert_json_to_arr(res);
              play_each_word();
              display_isl_text(res);
            },
            error: function(xhr)
            {
              console.log(xhr);
            }
        });
    };
  
     // start recognition
     recognition.start();
  
      // // ajax request to get the response from flask in json and play the words
      //   $.ajax({
      //       url:'/',
      //       type:'POST',
      //       data:{text:input},
      //       success: function(res)
      //       {
      //         convert_json_to_arr(res);
      //         play_each_word();
      //         display_isl_text(res);
      //       },
      //       error: function(xhr)
      //       {
      //         console.log(xhr);
      //       }
      //   });
    });
  
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
  
  