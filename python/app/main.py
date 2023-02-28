import tcp_socket as ts
import camera

tcp_port = 5000


# # # # # # # # # # # # 
def main():
    camera.cam_setup()
    ts.socket_receiver(tcp_port)
# # # # # # # # # # # #

# # # # # # # # # # # # 
if __name__ == "__main__":
    main()
# # # # # # # # # # # #     