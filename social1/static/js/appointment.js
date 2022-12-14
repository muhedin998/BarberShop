 //This is test
 const datum = document.getElementById("datum");
 const usluga = document.getElementById("usluga");
 const frizer = document.getElementById("frizer");
 const btn = document.getElementById("first_form_button")

 var duration = "{{ duration }}"
 console.log(duration*1000)
 var data = JSON.parse('{{filtered_list | escapejs}}');
 console.log(data)

 var compTermin = new Date()
 var lis = document.getElementById("id_vreme").getElementsByTagName("option");
 var id_vreme = document.getElementById("id_vreme")
 var za_brisanje = []
 

 //Iterate over all possible termins
 for (let i =0; i <lis.length; i++){

     const vreme_python = "{{ godina }},{{ mesec }},{{ dan }}".split(",")
     var danas = new Date()

     var b = lis[i].value.split(":")
     var term = new Date(vreme_python[0],vreme_python[1],vreme_python[2],b[0],b[1],b[2])
     console.log("Termin =",  term)

     //To be scheduled + duration to tetermin if there is enough time
     var porduzeni = new Date(term.getTime() + duration * 1000)

     //Iterate over all appoinments from database
     for (item in data){
       var c = data[item]["pocetak"].split(":")
       var zauzet_pocetak = new Date(vreme_python[0],vreme_python[1],vreme_python[2],c[0],c[1],c[2])

       var d = data[item]["kraj"].split(":")
       var zauzet_kraj = new Date(vreme_python[0],vreme_python[1],vreme_python[2],d[0],d[1],d[2])
       //Prevent todays expired termin of beeing selected
       if (datum.value == danas.getDate()){            
         if (danas.getTime() > term.getTime()){

           //check if we have already deleted that item
           if (!za_brisanje.includes(lis[i])){

             //appent to list for deleting
             za_brisanje.push(lis[i]);
           }
         }
       }
       if (porduzeni  > zauzet_pocetak.getTime()  && term < zauzet_kraj){
           lis[i].style.display = "none";
           if (!za_brisanje.includes(lis[i])){
             za_brisanje.push(lis[i]);
           }
       }
   }

}
//deleting taken termins
za_brisanje.forEach(zaBrisanje);
function zaBrisanje(el){
   el.remove()
   console.log(el)
}
