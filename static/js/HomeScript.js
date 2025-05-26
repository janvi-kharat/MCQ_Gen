var ImageArray = [];

    ImageArray[0] = "static/img/Homepg/notebook.svg";
    ImageArray[1] = "static/img/Homepg/onlinetest.svg";
    ImageArray[2] = "static/img/Homepg/question.svg";
    ImageArray[3] = "static/img/Homepg/exam.svg"


var time = 3000;
var i =0;
function ChangeImg()
{
    // Getting element by name of element
    document.imageSlide.src = ImageArray[i];
    if(i<ImageArray.length-1)
    {
        i++;
    }
    else
    {
        i=0;
    }
    console.log(ImageArray[i]);

    setTimeout('ChangeImg()',time);
}

window.onload = ChangeImg;



