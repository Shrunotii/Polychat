<?php 
session_start();
if(isset($_SESSION['unique_id'])){
    include_once "config.php";
    $outgoing_id = $_SESSION['unique_id'];
    $incoming_id = mysqli_real_escape_string($conn, $_POST['incomingId']);

    // Update the read status of messages from the specified incoming_id
    $sql = "UPDATE messages SET read_status = 1 WHERE incoming_msg_id = $outgoing_id AND outgoing_msg_id = $incoming_id";
    $query = mysqli_query($conn, $sql);
    if ($query) {
        echo "Messages marked as read successfully";
    } else {
        echo "Error marking messages as read: " . mysqli_error($conn);
    }
} else {
    header("location: ../login.php");
}
?>
