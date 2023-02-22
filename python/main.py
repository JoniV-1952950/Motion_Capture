import tcp_socket as ts
import camera

# # # # # # # # # # # # 
def main():
    camera.cam_setup()
    ts.socket_receiver()
# # # # # # # # # # # #

# # # # # # # # # # # # 
if __name__ == "__main__":
    main()
# # # # # # # # # # # #     