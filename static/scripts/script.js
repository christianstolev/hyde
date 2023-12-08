function log(html)
{
    function getCurrentTime() {
        const now = new Date();
      
        // Get hours, minutes, and seconds
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');
        const seconds = now.getSeconds().toString().padStart(2, '0');
      
        // Construct the time string
        const timeString = `${hours}:${minutes}:${seconds}`;
      
        return timeString;
    }
    
    $("#log").append("<b>[" + getCurrentTime() + "]</b> "+ html)
}

var waitingForCode = false
var pnumber = ""
function formatPhoneNumber(inputNumber) {
    let trimmedNumber = inputNumber.slice(1);
  
    // Add the country code
    let formattedNumber = '+46' + trimmedNumber;
  
    return formattedNumber;
  }
function handleKeyPress(event) {
    // Check if the pressed key is Enter
    if (event.key === 'Enter') {
      if(waitingForCode == true)
      {
        $.get('http://127.0.0.1:3000/verify?code=' + $("#num-input").val() + "&num=" + pnumber, function(data) {
            // Handle the successful response
            console.log('Data received:', data);
            if(data.includes("Failed"))
            {
                log('Något gick <span style="color: #d0546e"><b><u>fel</u></b></span> :(<br>')
            }
            else
            {
                log('Allt ser <span style="color: #54d054"><b>bra</b></span> ut :)<br>')
                window.location = "http://127.0.0.1:3000/scooters"

            }
        })
        .fail(function(xhr, status, error) {
            // This block will be executed if there is an error
            console.error('Error:', status, error);
        });
      }
      else
      {
        phone_number = encodeURIComponent(formatPhoneNumber($("#num-input").val()))
        pnumber = phone_number
        log('Kontrollerar..<br>')
            $.get('http://127.0.0.1:3000/login?num=' + (phone_number), function(data) {
                // Handle the successful response
                console.log('Data received:', data);
                if(data == "A verification code has been sent to the phone number you've entered.")
                {
                    log('Du kommer att få ett SMS på din mobiltelefon.<br>')
                    $("#num-input").val("")
                    waitingForCode = true
                }
                else
                {
                    log('Något gick <span style="color: #d0546e"><b><u>fel</u></b></span> :(<br>')
                }
            })
            .fail(function(xhr, status, error) {
                // This block will be executed if there is an error
                console.error('Error:', status, error);
            });
        }
      }
      // Perform the desired action here
      
}

$(document).ready(function() {
    $("#btn1").click(function() {
        log('Kontrollerar..<br>')
        $.get('http://127.0.0.1:3000/login', function(data) {
            // Handle the successful response
            console.log('Data received:', data);
            if(data == "valid")
            {
                log('Allt ser <span style="color: #54d054"><b>bra</b></span> ut :)<br>')
                window.location = "http://127.0.0.1:3000/scooters"
            }
            else
            {
                log('Något gick <span style="color: #d0546e"><b><u>fel</u></b></span> :(<br>')
            }
        })
        .fail(function(xhr, status, error) {
            // This block will be executed if there is an error
            console.error('Error:', status, error);
        });
    })
    $("#startBtn").click(function() {
        $.ajax({
            url: 'http://127.0.0.1:3000/get_scooters',
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                // Handle the successful response here
                data.forEach(function(scooter) {
                    scooter = scooter["scooter"]
                    $("#scList").append(`<div class="menu-list" onclick="onSelectScooter(this, ` + scooter["code"] + `)">
                    <i class="fi fi-rr-bolt boltanim" style="display: block; width: 100px; height: 100px; font-size: 30px;color: #9DB2BF;top: 22px;left: 14px;position: relative;"></i>
                    <p style="
            position: relative;
            top: -98px;
            left: 53px;
            font-family: sans-serif;
            color: white;
        "><span style="font-size: 18px;"><b>` + scooter["code"] + `</b></span><br><span style="font-size: 13px;">` + scooter["mac"] + `</span></p>
                </div>`)
                })
            },
            error: function(jqXHR, textStatus, errorThrown) {
                // Handle any errors here
                console.error('Error:', textStatus, errorThrown);
            }
        });
    });
    
    $("#btn2").click(function() {
        
        $("#INP-DIV").css("visibility", "visible");
    })
})

function onSelectScooter(scooter, ID)
{
    var cI = $(scooter).children().eq(0);

    if (cI.hasClass("fi-rr-bolt")) {
        cI.removeClass("fi-rr-bolt");
        cI.addClass("fi-sr-bolt");
        $.get('http://127.0.0.1:3000/begin_hack?code=' + ID, function(){})
        setTimeout(function(){
            cI.removeClass("fi-sr-bolt");
        }, 1000)
        cI.addClass("fi-sr-badge-check");
        setTimeout(function() {
            cI.removeClass("fi-sr-badge-check");
        }, 2000)
        cI.addClass("fi-rr-bolt");
    } else {
        cI.addClass("fi-rr-bolt");
        cI.removeClass("fi-sr-bolt");
    }
}