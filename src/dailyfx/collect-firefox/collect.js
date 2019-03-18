/*
Download announcements data from dailyfx.com
*/

function run() {
    urls = format();
    download(urls, 0);
}

function format() {
    ret = [];
    let date = new Date(2019, 2, 10);   // starting from March 10, 2019
    for (let i = 250; i > 0; --i) {     // for 250 weeks
        let y = date.getFullYear().toString();
        let m = (date.getMonth()+1).toString().padStart(2, "0");
        let d = date.getDate().toString().padStart(2, "0");
        ret.push(`https://www.dailyfx.com/calendar?previous=true&week=${y}/${m}${d}&currentweek=undefined&tz=0&currency=usd&importance=`);

        date.setDate(date.getDate()-7);
    }
    return ret;
}


function download(arr, i) {
    browser.downloads.download({
        "url": arr[i]
        , "filename": `dailyfx/${i}.html`
        , "conflictAction": "overwrite"
        , "saveAs": false
    }).then(function(){
        if(i+1 < arr.length){
            setTimeout(function(){
                download(arr, i+1);
            }, 1000);   // download at 1000ms interval
        }
    });
}

run();