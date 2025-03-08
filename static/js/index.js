function alertLowThreshold(){
    let threshold = document.getElementById("threshold_slider").value;
    confirmation = true
    if(threshold < 0.35 ){
        confirmation = confirm("Warning: Low threshold value may result in slow performance");
        if(confirmation){
            return true
        }else{
            return false
        }
    }else{
        return true
    }
}
