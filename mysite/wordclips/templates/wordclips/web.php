<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="ui.css">
</head>
<body>
<h1>Ventriloquy</h1>
<?php

   if(isset($_POST['BtnSubmit']))
   {
      echo "<h2>Input Text: </h2>";
      echo "<hr>";
?>
  <video  controls width="320" height="240" autoplay>
  <source src="movie.mp4" type="video/mp4">
  <source src="movie.ogg" type="video/ogg">
Your browser does not support the video tag.
</video>          
<?php
      echo "</br>Your Address :{$_POST['UserAddress']}";
      echo "<hr>";
   }

?>


<div>
<form  name="UserInformationForm" method="POST" action="#">
      <label for="UserAddress">Enter Text: </label>
      <br/>

      <textarea  name="UserAddress" ><?php echo $_POST['UserAddress']; ?></textarea>

      <br/><br/>
      <input name="BtnSubmit" type="submit" value="Submit">
</form>
</div>


</body>
</html>