import React from "react";
// import { Ethers } from "ether";
import logo from "./logo_bridge_v3.png";
import { Nav, NavLink,  NavMenu, NavBtn, NavBtnLink } from "./NavbarEle";
const Navbar = (props) => {
  let button;
  if (props.address === "") {
    button = "WIP";
  } else {
      button =      
      <span className="address">
      {props.address.toString().substring(0, 6)}…
      {props.address.toString().substring(props.address.toString().length - 4)}
    </span>;
  }
  return (
    <>
      <Nav>
        <NavLink to="/">
          <img
            src={logo}
            className="app_logo"
            alt="logo"
            style={{ height: 50 }}
          />
        </NavLink>

        <NavMenu>
          <NavLink to="/claim">claim</NavLink>
          <NavLink to="/warp">warp</NavLink>
          <NavLink to="/status">check status</NavLink>
        </NavMenu>
        <NavBtn onClick={() => props.set_trigger(true)}>{button}</NavBtn>
      </Nav>
    </>
  );
};

export default Navbar;
