<?php 
session_start();
if(isset($_SESSION['unique_id'])){
    include_once "config.php";
    $outgoing_id = $_SESSION['unique_id'];
    $incoming_id = mysqli_real_escape_string($conn, $_POST['incoming_id']);
    $output = "";
    $sql = "SELECT messages.*, users.img FROM messages LEFT JOIN users ON users.unique_id = messages.outgoing_msg_id
            WHERE (outgoing_msg_id = {$outgoing_id} AND incoming_msg_id = {$incoming_id})
            OR (outgoing_msg_id = {$incoming_id} AND incoming_msg_id = {$outgoing_id}) ORDER BY msg_id";
    $query = mysqli_query($conn, $sql);
    if(mysqli_num_rows($query) > 0){
        while($row = mysqli_fetch_assoc($query)){
            // Check if the message is from the current user or not
            $isOutgoing = $row['outgoing_msg_id'] === $outgoing_id;
            
            // Check if the message has been read
            $isRead = $row['read_status'] == 1 ? "read" : "";
            
            // Update the read status if the message is from the other user and has not been read
            if(!$isOutgoing && $row['read_status'] == 0) {
                // Mark the message as read in the database
                mysqli_query($conn, "UPDATE messages SET read_status = 1 WHERE msg_id = {$row['msg_id']}");
            }
            
            // Construct HTML for the message
            $output .= '<div class="chat ' . ($isOutgoing ? "outgoing" : "incoming") . ' ' . $isRead . '">
                            ' . ($isOutgoing ? '' : '<img src="php/images/'.$row['img'].'" alt="">') . '
                            <div class="details">
                                <p>'. $row['msg'] .'</p>
                            </div>
                        </div>';
        }
    }else{
        $output .= '<div class="text">No messages are available. Once you send message they will appear here.</div>';
    }
    echo $output;
}else{
    header("location: ../login.php");
}
?>