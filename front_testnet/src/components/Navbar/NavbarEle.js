import styled from "styled-components";
import { NavLink as Link } from "react-router-dom";


export const Nav = styled.nav`
  background: #614fff;
  height: 80px;
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0.5rem;
  z-index: 10;
`;

export const NavLink = styled(Link)`
  color: #fff;
  display: flex;
  align-items: center;
  text-decoration: none;
  padding: 0 1rem;
  height: 100%;
  cursor: pointer;

  &.active {
    color: #ffc107;
    font-weight: bold;
  }
`;

export const Logo = styled.div`
    width: 10px;
    height: 10px;
}`;



export const NavMenu = styled.div`
  display: flex;
  align-items: center;

  @media screen and (max-width: 600px) {
    position: absolute;
    bottom: 5rem;
    margin-left: 1.5rem;
    margin-right: 1.5rem;
    left: 0;
    right: 0;
    text-align: center;
    padding: 0.5rem;
    align-items: center;
    background: #614fff;
    border-radius:0.5rem ;
    transform: translateY(100%);
    transition: transform 0.3s ease-in-out;
    transform-origin: top;
    overflow: hidden;
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.2);
    z-index: 10;
    display: flex;
    justify-content: space-between;
    align-items: center;

  }
`;

export const NavBtn = styled.div`
  display: flex;
  align-items: center;
  margin-right: 24px;
  border-radius: 4px;
  background: #f6851b;
  padding: 10px 22px;
  margin-top: auto;
  margin-bottom: auto;
  height: 50%;
  color: #fff;
  cursor: pointer;
  &:hover {
    transition: all 0.2s ease-in-out;
    background: #e2761b;
  }
`;

export const NavBtnLink = styled(Link)`
  border-radius: 4px;
  background: #256ce1;
  padding: 10px 22px;
  color: #fff;
  border: none;
  outline: none;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  text-decoration: none;

  &:hover {
    transition: all 0.2s ease-in-out;
    background: #fff;
    color: #01011;
  }
`;
